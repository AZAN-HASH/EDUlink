from marshmallow import EXCLUDE, Schema, fields, validate


class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, load_only=True)
    school = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=120))
    location = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    role = fields.Str(load_default="student", validate=validate.OneOf(["student", "club_leader"]))


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
