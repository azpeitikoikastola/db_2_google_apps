# -*- coding: utf-8 -*-
from apiclient import errors


class File(object):

    # TODO check that fields exist and if they are of the correct type of data
    def __init__(self, *args, **kwargs):
        if args and kwargs:
            raise Warning('Use keyword args or a dict not both at the same '
                          'time.')
        elif args:
            for key, val in args:
                self.key = val
        elif kwargs:
            for key, val in kwargs:
                self.key = val

    @classmethod
    def _callback(cls, request_id, response, exception):
        if exception:
            # Handle error
            print exception
        else:
            print "Permission Id: %s" % response.get('id')

    @classmethod
    def _create(cls, data):
        return File(data)

    @classmethod
    def create(cls, ac, data):
        try:
            new_file = ac.service.groups().create(
                body=data, fields='id').execute()
            return File._create(new_file)
        except errors.HttpError as error:
            print 'An error occurred: %s' % error

    @classmethod
    def change_owner(cls, ac, g_file, email, callback=None):
            if isinstance(g_file, File):
                file_id = g_file.id
            else:
                file_id = g_file
            batch = ac.service.new_batch_http_request(
                callback=callback or cls._callback())
            user_permission = {'type': 'user', 'role': 'owner',
                               'emailAddress': email}
            batch.add(
                ac.service.permissions().create(
                    fileId=file_id,
                    body=user_permission,
                    fields='id',
                    transferOwnership=True))
            batch.execute()

    @classmethod
    def get(cls, ac, key):
        try:
            g_file = ac.service.groups().get(
                fileId=key).execute()
            return File._create(g_file)
        except errors.HttpError as error:
            print 'An error occurred getting group: %s' % error
# {
#   "kind": "drive#file",
#   "id": string,
#   "name": string,
#   "mimeType": string,
#   "description": string,
#   "starred": boolean,
#   "trashed": boolean,
#   "explicitlyTrashed": boolean,
#   "parents": [
#     string
#   ],
#   "properties": {
#     (key): string
#   },
#   "appProperties": {
#     (key): string
#   },
#   "spaces": [
#     string
#   ],
#   "version": long,
#   "webContentLink": string,
#   "webViewLink": string,
#   "iconLink": string,
#   "thumbnailLink": string,
#   "viewedByMe": boolean,
#   "viewedByMeTime": datetime,
#   "createdTime": datetime,
#   "modifiedTime": datetime,
#   "modifiedByMeTime": datetime,
#   "sharedWithMeTime": datetime,
#   "sharingUser": {
#     "kind": "drive#user",
#     "displayName": string,
#     "photoLink": string,
#     "me": boolean,
#     "permissionId": string,
#     "emailAddress": string
#   },
#   "owners": [
#     {
#       "kind": "drive#user",
#       "displayName": string,
#       "photoLink": string,
#       "me": boolean,
#       "permissionId": string,
#       "emailAddress": string
#     }
#   ],
#   "lastModifyingUser": {
#     "kind": "drive#user",
#     "displayName": string,
#     "photoLink": string,
#     "me": boolean,
#     "permissionId": string,
#     "emailAddress": string
#   },
#   "shared": boolean,
#   "ownedByMe": boolean,
#   "capabilities": {
#     "canEdit": boolean,
#     "canComment": boolean,
#     "canShare": boolean,
#     "canCopy": boolean,
#     "canReadRevisions": boolean
#   },
#   "viewersCanCopyContent": boolean,
#   "writersCanShare": boolean,
#   "permissions": [
#     permissions Resource
#   ],
#   "folderColorRgb": string,
#   "originalFilename": string,
#   "fullFileExtension": string,
#   "fileExtension": string,
#   "md5Checksum": string,
#   "size": long,
#   "quotaBytesUsed": long,
#   "headRevisionId": string,
#   "contentHints": {
#     "thumbnail": {
#       "image": bytes,
#       "mimeType": string
#     },
#     "indexableText": string
#   },
#   "imageMediaMetadata": {
#     "width": integer,
#     "height": integer,
#     "rotation": integer,
#     "location": {
#       "latitude": double,
#       "longitude": double,
#       "altitude": double
#     },
#     "time": string,
#     "cameraMake": string,
#     "cameraModel": string,
#     "exposureTime": float,
#     "aperture": float,
#     "flashUsed": boolean,
#     "focalLength": float,
#     "isoSpeed": integer,
#     "meteringMode": string,
#     "sensor": string,
#     "exposureMode": string,
#     "colorSpace": string,
#     "whiteBalance": string,
#     "exposureBias": float,
#     "maxApertureValue": float,
#     "subjectDistance": integer,
#     "lens": string
#   },
#   "videoMediaMetadata": {
#     "width": integer,
#     "height": integer,
#     "durationMillis": long
#   }
# }