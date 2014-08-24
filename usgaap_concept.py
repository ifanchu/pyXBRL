"""
This class is to represent the us-gaap concepts.
The concepts.csv was modified from the xlsx file, the "UGT *.xlsx" file was downloaded from fasb.org: http://www.fasb.org/cs/ContentServer?c=Page&pagename=FASB%2FPage%2FSectionPage&cid=1176160582432
Take the first sheet "Concept" from the xlsx.
Remove all columns after deprecatedLabel.
Remove all rows except for dei and us-gaap
"""
import os
import pickle

class UsGaapConcept(object):
    """
    This class represents one line in concepts.csv
    """
    def __init__(self,
                 _prefix,
                 _name,
                 _type,
                 _enumerations,
                 _substitutionGroup,
                 _balance,
                 _periodType,
                 _abstract,
                 _label,
                 _documentation,
                 _deprecatedLabel):
        self.prefix = _prefix
        self.name = _name
        self.type = _type
        self.enumerations = _enumerations
        self.substitutionGroup = _substitutionGroup
        self.balance = _balance
        self.periodType = _periodType
        self.abstract = True if _abstract else False
        self.label = _label
        self.documentation = _documentation
        self.deprecated = True if _deprecatedLabel else False

        self.tag = '{0}:{1}'.format(self.prefix, self.name)

    @classmethod
    def create_instance(cls, tokens):
        """
        Given a tuple of list, each token maps to init parameter
        """
        tokens = tuple([x.replace('"', '') for x in tokens])
        if len(tokens) != 11:
            return None
        return UsGaapConcept(
            tokens[0],
            tokens[1],
            tokens[2],
            tokens[3],
            tokens[4],
            tokens[5],
            tokens[6],
            tokens[7],
            tokens[8],
            tokens[9],
            tokens[10],
        )

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.tag == other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.tag)

class UsGaapConceptPool(object):
    """
    This class represents the entire collection of UsGaapConcept, provide convenience method to retrieve all concepts and access to specific concept.
    """
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    PICKLE_FILE_NAME = 'usgaap-concepts.pickle'
    pool = {}

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def _parse_concepts_to_pool(cls):
        concept_file_path = os.path.join(cls.CURRENT_DIR, 'us-gaap', 'concepts_2014.csv')
        if not os.path.isfile(concept_file_path):
            raise IOError('Concept file does not exist in {0}'.format(concept_file_path))
        with open(concept_file_path) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                line = line.strip()
                tokens = line.split('|')
                tokens = tokens[1:]     # remove the first token which is id
                if len(tokens) != 11:
                    diff = 11 - len(tokens)
                    tokens.extend([''] * diff)
                c = UsGaapConcept.create_instance(tokens)
                cls.pool[c.tag.upper()] = c

    @classmethod
    def _create_pickle(cls):
        if not cls.pool:
            cls._parse_concepts_to_pool()
        with open(cls.PICKLE_FILE_NAME, 'wb') as f:
            pickle.dump(cls.pool, f)

    @classmethod
    def _has_pickle(cls):
        return os.path.exists(cls.PICKLE_FILE_NAME)

    @classmethod
    def _load_pickle(cls):
        if not cls._has_pickle():
            cls._create_pickle()
        with open(cls.PICKLE_FILE_NAME, 'rb') as f:
            cls.pool = pickle.load(f)

    @classmethod
    def get(cls, tag):
        """
        tag format is <prefix>:<name>, eg. dei:DocumentType
        """
        if not cls.pool:
            cls._load_pickle()
        if tag.upper() not in cls.pool:
            return None
        return cls.pool[tag.upper()]

    @classmethod
    def get_all_tags(cls):
        if not cls.pool:
            cls._load_pickle()
        return sorted([x.tag for x in cls.pool.values()])

if __name__ == '__main__':
    UsGaapConceptPool._load_pickle()
    obj = UsGaapConceptPool.get('dei:documentype')
