from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    # The DataRequired() function below makes the Form
    # impossible to send if any of the field are empty
    username = StringField('Nome de usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Login')

class RelatDuplLiquidForm(FlaskForm):
    cedente_id = StringField('Número da C/C', validators=[DataRequired()])
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

class RelatDuplRecebForm(FlaskForm):
    cedente_id = StringField('Número da C/C', validators=[DataRequired()])
    situation = SelectField(
        # TODO change the js script to work on this page
        'Situação', 
        choices=[
            ('1','A vencer'),
            ('2','Vencidas'),
            ('3','Geral')
        ],
          validators=[Optional()]
    )
    start_date = DateField('Período (de)', validators=[Optional()])
    end_date = DateField('Período (a)', validators=[Optional()])
    submit = SubmitField('Abrir')

class RelatGeralForm(FlaskForm):
    cedente_id = StringField('Número do Cedente', validators=[DataRequired()])
    cedente_type = StringField('Tipo', validators=[DataRequired()])
    start_date = DateField('Período (de)', validators=[Optional()])
    end_date = DateField('Período (a)', validators=[Optional()])
    interval = SelectField(
        'Intervalo', 
        choices=[
            ('3','3 Dias'),
            ('15','15 Dias'),
            ('30','30 Dias'),
            ('custom','Personalizado')
        ],
          validators=[Optional()]
    )
    submit = SubmitField('Abrir')