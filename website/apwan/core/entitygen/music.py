# pylint: disable=R0911

from __future__ import absolute_import
import re
from django.conf import settings
import musicbrainzngs
from website.apwan.core.entitygen import EntityGenerator, registry
from website.apwan.models.entity import Entity
from website.apwan.models.entity_reference import EntityReference
from website.apwan.models.recipient import Recipient
from website.apwan.models.recipient_reference import RecipientReference
from website.apwan import USERAGENT_NAME, USERAGENT_VERSION, USERAGENT_CONTACT

musicbrainzngs.set_useragent(USERAGENT_NAME,
                             USERAGENT_VERSION,
                             USERAGENT_CONTACT)
musicbrainzngs.set_rate_limit()

__author__ = 'Dean Gardiner'


ALLOWED_RELEASE_TYPES = ['Album', 'Single', 'EP']


class MusicEntityGenerator(EntityGenerator):
    class Meta:
        key = 'music'
        recipient_types = [Recipient.TYPE_MUSIC_ARTIST, Recipient.TYPE_MUSIC_LABEL]

    @staticmethod
    def entity_lookup(artist, album=None, track=None):
        query = MusicEntityGenerator._build_query(artist, album, track)
        results = MusicEntityGenerator._request(query, artist, album, track)

        # Parse result into (artist, releases, recording)
        if results:
            if track:
                results = results['recording-list']
            elif album:
                results = results['release-list']
            else:
                results = results['artist-list']

            if len(results) > 0:
                _recording = None
                _releases = None
                _artist = None

                if track:
                    (_recording, _releases) = \
                        MusicEntityGenerator._parse_recordings(results)
                    _artist = musicbrainzngs.get_artist_by_id(
                        _recording['artist-credit'][0]['artist']['id']
                    )['artist']
                elif album:
                    _artist, _releases = \
                        MusicEntityGenerator._parse_releases(results)
                elif artist:
                    _artist = results[0]

                return _artist, _releases, _recording
        return None

    @staticmethod
    def entity_create(artist, album=None, track=None):
        l_artist, l_releases, l_recording = \
            MusicEntityGenerator.entity_lookup(artist, album, track)

        #
        # Create Artist Recipient
        #
        _, recipient, _ = EntityGenerator.db_create_recipient(
            l_artist['id'], l_artist['name'],
            RecipientReference.TYPE_MUSICBRAINZ,
            Recipient.TYPE_MUSIC_ARTIST
        )

        #
        # Create Artist Entity
        #
        _, e_artist, e_artist_created = \
            EntityGenerator.db_create_entity(
                l_artist['id'],
                EntityReference.TYPE_MUSICBRAINZ, Entity.TYPE_MUSIC,
                artist=l_artist['name']
            )
        if e_artist_created:
            print "Artist Created"
            e_artist.recipient.add(recipient)

        #
        # Create Album Entity
        #
        e_album = None
        if l_releases:
            _, e_album, e_album_created = \
                EntityGenerator.db_create_entity(
                    l_releases[0][0]['id'],
                    EntityReference.TYPE_MUSICBRAINZ, Entity.TYPE_MUSIC,
                    artist=l_artist['name'],
                    album=l_releases[0][0]['title'],
                    parent=e_artist
                )
            if e_album_created:
                print "Album Created"
                e_album.recipient.add(recipient)

        #
        # Create Track Entity
        #
        e_track = None
        if l_recording:
            _, e_track, e_track_created = \
                EntityGenerator.db_create_entity(
                    l_recording['id'],
                    EntityReference.TYPE_MUSICBRAINZ, Entity.TYPE_MUSIC,
                    artist=l_artist['name'],
                    album=l_releases[0][0]['title'],
                    track=l_recording['title'],
                    parent=e_album
                )
            if e_track_created:
                print "Track Created"
                e_track.recipient.add(recipient)

        #
        # Return Entity
        #
        if e_track:
            return e_track
        elif e_album:
            return e_album
        elif e_artist:
            return e_artist
        return None

    @staticmethod
    def _build_query(artist, album=None, track=None):
        artist = MusicEntityGenerator._escape_query_field(artist)
        album = MusicEntityGenerator._escape_query_field(album)
        track = MusicEntityGenerator._escape_query_field(track)

        query = None
        if track and album:
            query = track + ' artist:' + artist + ' album:' + album
        elif track:
            query = track + ' artist:' + artist
        elif album:
            query = album + ' artist:' + artist
        else:
            query = 'artist:' + artist

        return query

    @staticmethod
    def _escape_query_field(text):
        if text is None:
            return None
        return re.sub(r'([+\-&|!(){}\[\]\^"~*?:\\])', r'\\\1', text)

    @staticmethod
    def _request(query, artist, album=None, track=None):
        results = None
        if track:
            results = musicbrainzngs.search_recordings(query=query)
        elif album:
            results = musicbrainzngs.search_releases(query=query)
        elif artist:
            results = musicbrainzngs.search_artists(query=query)

        return results

    @staticmethod
    def _get_labels_by_release(release_id):
        labels = musicbrainzngs.browse_labels(release_id)
        if 'label-list' in labels:
            return labels['label-list']
        return None

    @staticmethod
    def _valid_release(rel):
        if 'status' not in rel or rel['status'] != 'Official':
            return False

        if 'release-group' not in rel:
            return False

        if 'primary-type' not in rel['release-group']:
            return False

        if rel['release-group']['primary-type'] not in ALLOWED_RELEASE_TYPES:
            return False

        if 'type' in rel['release-group']:
            if rel['release-group']['type'] not in ALLOWED_RELEASE_TYPES:
                return False

        if 'label-info-list' not in rel:
            return False

        return True

    @staticmethod
    def _validate_score(top, current):
        return top is None or current['ext:score'] == top['ext:score']

    @staticmethod
    def _parse_recordings(recordings):
        _recording = None
        _results = []

        for recording in recordings:
            if MusicEntityGenerator._validate_score(_recording, recording):
                _recording = recording

                recording_releases = musicbrainzngs.browse_releases(
                    recording=recording['id'],
                    includes=['labels', 'release-groups']
                )

                # Find all valid releases (Official releases)
                for rel in recording_releases['release-list']:
                    if MusicEntityGenerator._valid_release(rel):
                        _results.append((rel, rel['label-info-list']))

                # Clean up recording data
                if 'release-list' in recording:
                    recording.pop('release-list')
            else:
                break

        return _recording, _results

    @staticmethod
    def _parse_releases(releases):
        _release = None
        _results = []

        for release in releases:
            if MusicEntityGenerator._validate_score(_release, release):
                if _release is None:
                    _release = release

                # Find all valid releases (Official releases)
                if MusicEntityGenerator._valid_release(release):
                    _results.append((release, release['label-info-list']))

        _artist = musicbrainzngs.get_artist_by_id(
            _release['artist-credit'][0]['artist']['id']
        )['artist']
        return _artist, _results

if settings.FRUCTUS_KEYS:
    registry.register(MusicEntityGenerator())
