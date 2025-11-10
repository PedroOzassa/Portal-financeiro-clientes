from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    # The DataRequired() function below makes the frontend's Form impossible to send if the field is empty
    username = StringField('Nome de usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Login')
class RelatDuplLiquidForm(FlaskForm):
    cedente_id = StringField('Número da C/C', validators= [DataRequired()])
    interval = SelectField(
        'Intervalo', 
        choices=[
            ('3','3 Dias'),
            ('15','15 Dias'),
            ('30','30 Dias'),
            ('60','60 Dias'),
            ('custom','Personalizado')
        ],
          validators=[Optional()]
    )
    start_date = DateField('Período (de)', validators=[Optional()])
    end_date = DateField('Período (a)', validators=[Optional()])
    submit = SubmitField('Abrir')

