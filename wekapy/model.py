from .helper import run_process
from .WekaPyException import WekaPyException
import fileinput
import os

class Model:
    def __init__(self, name, trait, classifier_type=None, max_memory=1500, classpath=None, verbose=False):
        if classifier_type is None or not isinstance(classifier_type, str):
            raise WekaPyException("A classifier type is required for construction.")
        if not isinstance(max_memory, int):
            raise WekaPyException("'max_memory' argument must be of type (int).")
        self.id = name
        self.trait = trait
        self.arff_dir = os.path.join(os.path.dirname(__file__), 'temp')
        self.classpath = classpath
        self.classifier = classifier_type
        self.max_memory = max_memory
        self.samples = []
        self.ids = []
        self.feat = []
        self.predictions = {}
        self.time_taken = 0.0
        self.verbose = verbose
        self.trained = False
        self.model_file = None
        self.training_file = None
        self.test_file = None
        if not os.path.exists(self.arff_dir):
            os.makedirs(self.arff_dir)

    # Generate an ARFF file from a list of instances
    def create_arff(self, instances, data_type):

        p = os.path.join(self.arff_dir, f"{self.id}.arff")

        output_arff = open(p, "w")
        output_arff.write("@relation " + str(self.id) + "\n")
        for i, s in enumerate(instances):
            if i == 0:
                output_arff.write(f"\t@attribute {self.trait} numeric\n")
                for name in self.feat:
                    output_arff.write(f"\t@attribute {name} numeric\n")
                output_arff.write("\n@data\n")
            str_to_write = "0,"
            for j, val in enumerate(s):
                if j == 0:
                    str_to_write = str_to_write + str(val)
                else:
                    str_to_write = str_to_write + "," + str(val)
            output_arff.write(str_to_write + "\n")
        output_arff.close()

        if data_type == "test":
            self.test_file = p

    # Load a model, if it exists, and set this as the currently trained model for this
    # Model instance.
    def load_model(self, model_file):
        if os.path.exists(model_file):
            self.model_file = model_file
            self.trained = True
        else:
            raise WekaPyException("Your model could not be found.")

    def set_samples(self, samples):
        self.samples = list(samples.values())
        self.ids = list(samples.keys())

    # Generate predictions from the trained model from test features in an ARFF file
    def predict(self, test_file=None, instances=None, model_file=None):

        self.create_arff(self.samples, "test")

        options = ["java", "-Xmx{}M".format(str(self.max_memory))]
        if self.classpath is not None:
            options.extend(["-cp", self.classpath])
        options.extend(["weka.classifiers." + self.classifier, "-T", self.test_file, "-l", self.model_file, "-p", "0", "-c", "1"])

        process_output, self.time_taken = run_process(options)

        lines = process_output.split("\n")
        instance_predictions = {}
        i = 0

        for line in lines:
            pred = line.split()
            if len(pred) >= 4 and not pred[0].startswith("=") and not pred[0].startswith("inst"):
                n = float(pred[2])
                instance_predictions[self.ids[i]] = 0 if n < 0 else 1 if n > 1 else n
                i += 1
        self.predictions = instance_predictions
        if self.verbose:
            print("Testing complete (time taken = {:.2f}s).".format(self.time_taken))
        return instance_predictions
