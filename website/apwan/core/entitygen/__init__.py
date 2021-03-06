import unicodedata
from website.apwan.models.entity import Entity
from website.apwan.models.entity_reference import EntityReference
from website.apwan.models.recipient import Recipient
from website.apwan.models.recipient_reference import RecipientReference

SPECIAL_PHRASES = [
    '~', '`', '!', '@', '#', '$', '%', '^',
    '&', '*', '(', ')', '_', '-', '+', '=',
    ',', '.', '/', '?',
    ':', ';', '"', "'",
    '[', ']', '{', '}',
    '\\', '|',

    u"\u2019",

    'and'
]


def search_strip(text):
    if text is None:
        return None

    if type(text) is unicode:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')

    for char in SPECIAL_PHRASES:
        text = text.replace(char, '')

    return text.strip()


def search_like(text):
    if text is None:
        return None

    if type(text) is unicode:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')

    for char in SPECIAL_PHRASES:
        text = text.replace(char, '%')

    text = text.replace(' ', '%')
    return text.strip('%')


class EntityGenerator():
    class Meta:
        key = None
        recipient_types = None

    def __init__(self):
        pass

    @staticmethod
    def db_create_recipient(key, title, ref_type, recipient_type):
        # Search for id in recipient references
        reference_filter = RecipientReference.objects.filter(
            type=ref_type,
            key=key
        )
        reference_exists = len(reference_filter) == 1
        if reference_exists:
            return reference_filter[0], reference_filter[0].recipient, False

        # Create Recipient
        recipient = Recipient.objects.create(
            title=title,
            s_title=search_strip(title),
            type=recipient_type
        )

        # Create Reference
        reference = RecipientReference.objects.create(
            recipient=recipient,
            type=ref_type,
            key=key
        )

        return reference, recipient, True

    @staticmethod
    def db_create_entity(entity_id, ref_type, entity_type, title=None, year=None,
                         artist=None, album=None, track=None, parent=None):

        reference_filter = EntityReference.objects.filter(
            type=ref_type,
            key=entity_id
        )
        reference_exists = len(reference_filter) == 1
        if reference_exists:
            print "reference exists", entity_id
            return reference_filter[0], reference_filter[0].entity, False

        # Create Entity
        entity = Entity.objects.create(
            parent=parent,
            # Music
            artist=artist,
            album=album,
            track=track,
            # TV Show, Movie, Game
            title=title,
            # Movie
            year=year,
            # Search Fields
            s_title=search_strip(title),
            s_artist=search_strip(artist),
            s_album=search_strip(album),
            s_track=search_strip(track),
            type=entity_type
        )

        # Create Reference
        reference = EntityReference.objects.create(
            entity=entity,
            type=ref_type,
            key=entity_id
        )

        return reference, entity, True


class EntityGeneratorRegistry:
    def __init__(self):
        self.entity_generators = {}  # [__generator_key__] -> [EntityGenerator]
        self.recipient_type_map = {}  # [Recipient.type] -> [EntityGenerator]

    def register(self, entity_generator):
        if not isinstance(entity_generator, EntityGenerator):
            raise TypeError()
        if entity_generator.Meta.key in self.entity_generators:
            print "entity_generator already registered"
            return
        self.entity_generators[entity_generator.Meta.key] = entity_generator

        for recipient_type in entity_generator.Meta.recipient_types:
            self.recipient_type_map[recipient_type] = entity_generator.Meta.key

    def __getitem__(self, key):
        if type(key) == str:
            return self.entity_generators[key]
        elif type(key) == int:
            return self.entity_generators[self.recipient_type_map[key]]

    def __setitem__(self, key, value):
        raise Exception()

    def __delitem__(self, key):
        raise Exception()

    def __contains__(self, key):
        return key in self.entity_generators

    def __len__(self):
        return len(self.entity_generators)

registry = EntityGeneratorRegistry()
