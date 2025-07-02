from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FileField, HiddenField, SubmitField
from wtforms.validators import DataRequired

class EffectForm(FlaskForm):
    effect_type = SelectField(
        'Effect Type',
        choices=[
            ('text', 'Text Effect'),
            ('picture', 'Picture Effect'),
            ('solution', 'Solution Effect'),
            ('animation', 'Animation Effect')
        ],
        validators=[DataRequired()]
    )
    name = StringField('Effect Name', validators=[DataRequired()])
    preview_image = FileField('Preview Image')
    code = TextAreaField('Effect Code', validators=[DataRequired()])
    is_public = BooleanField('Make this effect public', default=True)
    effect_id = HiddenField()
    submit = SubmitField('Save') 