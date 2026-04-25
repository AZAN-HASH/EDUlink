from marshmallow import EXCLUDE, Schema, fields, validate


class ClubCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    description = fields.Str(load_default=None, allow_none=True)
    school_id = fields.Int(required=True)
    banner_url = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=255))
