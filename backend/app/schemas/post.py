from marshmallow import EXCLUDE, Schema, fields, validate


class PostCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True, validate=validate.Length(min=3, max=160))
    description = fields.Str(required=True, validate=validate.Length(min=5))
    code_snippet = fields.Str(load_default=None, allow_none=True)
    club_id = fields.Int(load_default=None, allow_none=True)


class CommentCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    content = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
