# An experiment with train+devel/test sets using pre-selected parameter values

from Pipeline import *
import os

# define shortcuts for commonly used files
PARSE="stanford-newMC-intra"
TOK="split-McClosky"
CORPUS_DIR="/usr/share/biotext/UnmergingProject/source"
TEST_FILE=CORPUS_DIR+"/with-heads/bioinfer-test-"+PARSE+".xml"
TRAIN_AND_DEVEL_FILE=CORPUS_DIR+"/with-heads/bioinfer-train-and-devel-"+PARSE+".xml"

# trigger examples
TRIGGER_EXAMPLEDIR="/usr/share/biotext/UnmergingProject/results/examples-"+PARSE
TRIGGER_TEST_EXAMPLE_FILE=TRIGGER_EXAMPLEDIR+"/trigger-test-examples-"+PARSE
TRIGGER_TRAIN_AND_DEVEL_EXAMPLE_FILE=TRIGGER_EXAMPLEDIR+"/trigger-train-and-devel-examples-"+PARSE
TRIGGER_IDS="bioinfer-trigger-ids"

# edge examples
EDGE_EXAMPLEDIR=TRIGGER_EXAMPLEDIR
EDGE_TEST_EXAMPLE_FILE=EDGE_EXAMPLEDIR+"/edge-test-examples-"+PARSE
EDGE_TRAIN_AND_DEVEL_EXAMPLE_FILE=EDGE_EXAMPLEDIR+"/edge-train-and-devel-examples-"+PARSE
EDGE_IDS="bioinfer-edge-ids"

# choose a name for the experiment
EXPERIMENT_NAME="UnmergingProject/results/test-set-"+PARSE
WORKDIR="/usr/share/biotext/GeniaChallenge/"+EXPERIMENT_NAME

TRIGGER_CLASSIFIER_PARAMS="c:50000"
EDGE_CLASSIFIER_PARAMS="c:5000000"
EDGE_FEATURE_PARAMS="style:typed,directed,no_linear,entities,noMasking,maxFeatures,bioinfer_limits"
#RECALL_BOOST_PARAM=0.7

# start the experiment
workdir(WORKDIR, False) # Select a working directory, don't remove existing files
copyIdSetsToWorkdir(TRIGGER_EXAMPLEDIR+"/bioinfer-trigger-ids")
copyIdSetsToWorkdir(EDGE_EXAMPLEDIR+"/bioinfer-edge-ids")
log() # Start logging into a file in working directory

print >> sys.stderr, "BioInfer Test Set"
print >> sys.stderr, "Trigger params", TRIGGER_CLASSIFIER_PARAMS
#print >> sys.stderr, "Recall Booster params", str(RECALL_BOOST_PARAM)
print >> sys.stderr, "Edge params", EDGE_CLASSIFIER_PARAMS
###############################################################################
# Triggers
###############################################################################
#c = CSCConnection(EXPERIMENT_NAME+"/trigger-model", "jakrbj@murska.csc.fi")
best = optimize(Cls, Ev, TRIGGER_TRAIN_AND_DEVEL_EXAMPLE_FILE, TRIGGER_TEST_EXAMPLE_FILE,\
    TRIGGER_IDS+".class_names", TRIGGER_CLASSIFIER_PARAMS, "test-trigger-param-opt", None)#, c)
# The evaluator is needed to access the classifications (will be fixed later)
ExampleUtils.writeToInteractionXML(TRIGGER_TEST_EXAMPLE_FILE, best[2], TEST_FILE, "test-predicted-triggers.xml", TRIGGER_IDS+".class_names", PARSE, TOK)
# NOTE: Merged elements must not be split, as recall booster may change their class
#ix.splitMergedElements("devel-predicted-triggers.xml", "devel-predicted-triggers.xml")
ix.recalculateIds("test-predicted-triggers.xml", "test-predicted-triggers.xml", True)

###############################################################################
# Edges
###############################################################################
#boostedTriggerFile = "test-predicted-triggers-boost.xml"
#RecallAdjust.run("test-predicted-triggers.xml", RECALL_BOOST_PARAM, boostedTriggerFile)
#ix.splitMergedElements(boostedTriggerFile, boostedTriggerFile)
#ix.recalculateIds(boostedTriggerFile, boostedTriggerFile, True)
# Build edge examples
#MultiEdgeExampleBuilder.run(boostedTriggerFile, "test-edge-examples", PARSE_TOK, PARSE_TOK, EDGE_FEATURE_PARAMS, EDGE_IDS)
MultiEdgeExampleBuilder.run("test-predicted-triggers.xml", "test-edge-examples", PARSE, TOK, EDGE_FEATURE_PARAMS, EDGE_IDS)
# Classify with pre-defined model
#c = CSCConnection(EXPERIMENT_NAME+"/edge-model", "jakrbj@murska.csc.fi")
best = optimize(Cls, Ev, EDGE_TRAIN_AND_DEVEL_EXAMPLE_FILE, "test-edge-examples",\
    EDGE_IDS+".class_names", EDGE_CLASSIFIER_PARAMS, "test-edge-param-opt", None)#, c)
# Write to interaction xml
xmlFilename = "test-predicted-edges.xml"
ExampleUtils.writeToInteractionXML("test-edge-examples", best[2], boostedTriggerFile, xmlFilename, "genia-edge-ids.class_names", PARSE_TOK, PARSE_TOK)
ix.splitMergedElements(xmlFilename, xmlFilename)
ix.recalculateIds(xmlFilename, xmlFilename, True)
# EvaluateInteractionXML differs from the previous evaluations in that it can
# be used to compare two separate GifXML-files. One of these is the gold file,
# against which the other is evaluated by heuristically matching triggers and
# edges. Note that this evaluation will differ somewhat from the previous ones,
# which evaluate on the level of examples.
EvaluateInteractionXML.run(Ev, xmlFilename, TEST_FILE, PARSE, TOK)

###############################################################################
# Post-processing
###############################################################################
#prune.interface(["-i",xmlFilename,"-o","pruned.xml","-c"])
#unflatten.interface(["-i","pruned.xml","-o","unflattened.xml","-a",PARSE_TOK,"-t",PARSE_TOK])
## Output will be stored to the geniaformat-subdirectory, where will also be a
## tar.gz-file which can be sent to the Shared Task evaluation server.
#gifxmlToGenia("unflattened.xml", "geniaformat")
