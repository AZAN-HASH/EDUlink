from marshmallow import EXCLUDE, Schema, fields, validate


class MessageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    body = fields.Str(required=True, validate=validate.Length(min=1, max=3000))
