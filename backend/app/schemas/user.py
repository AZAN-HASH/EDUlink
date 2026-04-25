from marshmallow import EXCLUDE, Schema, fields, validate


class UserUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(load_default=None, allow_none=True, validate=validate.Length(min=3, max=50))
    bio = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=500))
    school = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=120))
    location = fields.Str(load_default=None, allow_none=True, validate=validate.Length(min=2, max=120))
    profile_picture = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=255))
    role = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(["student", "club_leader", "admin"]))
