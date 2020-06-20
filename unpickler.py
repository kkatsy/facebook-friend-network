import pickle

# see contents of pickled files
FILENAME = "name_to_id.pickle"
pickle_off = open(FILENAME,"rb")
contents = pickle.load(pickle_off)

print(contents)
