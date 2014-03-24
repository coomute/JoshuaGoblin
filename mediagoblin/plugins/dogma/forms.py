# -*- coding: utf-8 -*-
# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#FORMS
import wtforms
from mediagoblin.plugins.wtform_html5.wtforms_html5 import (TextField, IntegerField, DateField,
        TextAreaField, DateRange)
#multiple upload
from wtforms.widgets import html_params, HTMLString

from mediagoblin.plugins.dogma_lib.countries import countries_list
from mediagoblin.plugins.dogma_lib.lib import complete_band_list
from mediagoblin.tools.text import tag_length_validator
from mediagoblin.tools.licenses import licenses_as_choices
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from mediagoblin.tools.translate import fake_ugettext_passthrough as _
from cgi import escape


#
#
# 	En attente de l'implémentation de la traduction les classes d'origine 
#	sont préfixées avec un "XX", les classes "utilisées" héritent
#	de la classe d'origine :
#	 	DogmaTracks(wtforms.Form): devient -> XXDogmaTracks(wtforms.Form):
#		et la classe utilisée contenant les textes en français sera : 
#			DogmaTracks(XXDogmaTracks):
#
#	L'ajout de membres ne contenant pas de textes affichables doivent être implémentés
#	uniquement dans les classes "XX".
#	L'ajout de membres contenant du texte doivent être implémentées dans les classes
#	en "ZONE des Classes modifiées" en français et OBLIGATOIREMENT implémentés dans 
#	les classes correspondantes "XX" en anglais avec le _( ... )
#	Toutes classes nouvelles suivront les mêmes règles.
#	Conclusion : à chaque CLASS "XX" doit correspondre
#	             une classe de même nom sans "XX".
#
#   De cette façon : lors de l'implémentation de la traduction automatique, il suffira de
#   supprimer toutes les classes ayant comme héritage une classe "XX"
#	et supprimer le "XX" devant les classes ci-dessous
#

#
#  fonctions de confort pour allèger le code
#
def DogmaUtilMKBOOK() :
    return u"""Vous pouvez utiliser les 
                      <a href="http://daringfireball.net/projects/markdown/basics" target="_blank">
                      Outils</a> pour améliorer la mise en page du texte."""

# --------

#Custom multiple file input field made by pythonsnake
class LocationInput(object):
    def __call__(self, field, **kwargs):
        if field.flags.required:
            kwargs['required'] = 'required'
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
            #This counter is needed when there's multiple field on the same page so JS can now where it is
            kwargs['data-counter'] = '_0'
        html = [u'<div class="location" id="location_0">\
                <input %s />' % html_params(type="text", name=field.name, class_="city_search city_search_0",  **kwargs)]
        if field.quick_location:
            html.append(u'<button class="button_action copy_band_location" type="button">%s</button>' % field.quick_location)
        html.append(u'<div id="SuggestBoxElement_0"></div>\
                      </div>')
        return HTMLString(u''.join(html))

class LocationField(wtforms.FileField):
    widget = LocationInput()

    def __init__(self,label=None, validators=None,quick_location=None, **kwargs):
        super(LocationField, self).__init__(label, validators, **kwargs)
        self.quick_location = quick_location


class DatePickerInput(object):
    def __call__(self, field, **kwargs):
        if field.flags.required:
            kwargs['required'] = 'required'
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        if field.pattern :
           kwargs['pattern'] = field.pattern

        html = [u'<div class="datePicker  '+field.custom_class+'" data-millis="'+field.millis+'" ></div>\
                <input %s />' % html_params(type="text", name=field.name, class_="date_picker_input",  **kwargs)]
        if field.quick_date:
            html.append(u'<button class="button_action copy_band_date" type="button">%s</button>' % field.quick_date)
        return HTMLString(u''.join(html))

class DatePickerField(wtforms.FileField):
    widget = DatePickerInput()

    def __init__(self,label=None, validators=None,quick_date=None, millis=u'', custom_class=u'', pattern=None, **kwargs):
        super(DatePickerField, self).__init__(label, validators, **kwargs)
        self.quick_date = quick_date
        self.millis = millis
        self.pattern = pattern
        self.custom_class = custom_class


class MultipleFileInput(object):
    def __call__(self, field, **kwargs):
        value = field._value()
        if field.flags.required:
            kwargs['required'] = 'required'
        html = [u'<input %s>' % html_params(name='file[]', id='multi_file_input', type='file', 
                                                  multiple=True, **kwargs)]
        if value:
            kwargs.setdefault('value', value)
        return HTMLString(u''.join(html))

class MultipleFileField(wtforms.FileField):
    widget = MultipleFileInput()


class XXLocationForm(wtforms.Form):
    place_0 = LocationField(
            _('City :'),
            [wtforms.validators.Optional()],
            description=_("Type the name of the city and select one in the list (you must select a country first)"),
            quick_location = _("Same location as the band"),
                )
    latitude_0 = wtforms.HiddenField(_('Latitude'),
                  )
    longitude_0 = wtforms.HiddenField(
                  _('Longitude'),
                  )

class LocationForm(XXLocationForm):
    place_0 = LocationField(
            'Ville :',
            [wtforms.validators.Optional()],
            description=u"Entrez le nom de la ville ou sélectionnez-la dans la liste (vous devez avoir choisi un pays auparavant.)",
            quick_location = u"Même localisation que le groupe",
                )

class XXDogmaTracks(wtforms.Form):
    title_0 = TextField(
        _('Title'),
        [wtforms.validators.Length(min=0, max=500)],
        description=_(
          "Leave blank if the title is the name of the file."))
    license_0 = wtforms.SelectField(
        _('License'),
        [wtforms.validators.NoneOf('_None', _("you must choose a license"))],
        choices=licenses_as_choices())
    composers_0 = TextField(
        _('Composer(s)'),
        [tag_length_validator],
        description=_(
          "Separate names by commas."))
    authors_0 = TextField(
        _('Author(s)'),
        [tag_length_validator],
        description=_(
          "Separate names by commas."))
    performerNo0_0 = TextField(
        _('Extra Performer'))
    performer_rolesNo0_0 = TextField(
        _('plays'))
    tags_0 = TextField(
        _('Tags for this tracks'),
        [tag_length_validator],
        description=_(
          "Separate tags by commas. (they will be added to the global tags)"))
    description_0 = wtforms.TextAreaField(
        _('Description of this work'),
        description=_("""You can use
                      <a href="http://daringfireball.net/projects/markdown/basics">
                      Markdown</a> for formatting."""),
        id="wmd-input_0"
        )

class DogmaTracks(XXDogmaTracks):
    title_0 = TextField(
        u'Titre',
        [wtforms.validators.Length(min=0, max=500)],
        description=u"Laisser ce champs vide si le titre est le nom du fichier.")
    license_0 = wtforms.SelectField(
        u'Licence',
        [wtforms.validators.NoneOf('_None', u"Vous devez choisir une licence")],
        choices=licenses_as_choices())
    composers_0 = TextField(
        u'Compositeur(s)',
        [tag_length_validator],
        description=u"Séparez les noms par des virgules.")
    authors_0 = TextField(
        u'Auteur(s)',
        [tag_length_validator],
        description=u"Séparez les noms par des virgules.")
    performerNo0_0 = TextField(
        _('Extra Performer'))
    performer_rolesNo0_0 = TextField(
        _('plays'))
    tags_0 = TextField(
        u'Tags pour ce titre',
        [tag_length_validator],
        description=u"Séparez les tags par des virgules. (Ils seront ajoutés aux tags globaux)")
    description_0 = wtforms.TextAreaField(
        u'Description de ce titre',
        description=DogmaUtilMKBOOK(),
#        description="""Vous pouvez utiliser les 
#                      <a href="http://daringfireball.net/projects/markdown/basics">
#                      Outils</a> pour mettre ne page le texte.""",
        id="wmd-input_0"
        )


class XXDogmaTracksGlobal(wtforms.Form):
    composers = TextField(
        _('Composer(s) for ALL tracks'),
        [tag_length_validator],
        description=_(
          "Separate names by commas."))
    authors = TextField(
        _('Author(s) for ALL tracks'),
        [tag_length_validator],
        description=_(
          "Separate names by commas."))
    tags = TextField(
        _('Tags for ALL tracks'),
        [tag_length_validator],
        description=_(
          "Separate tags by commas. Songs' tags will be added to global tags."))
    license = wtforms.SelectField(
        _('License for ALL tracks'),
        [wtforms.validators.Optional()],
        choices=licenses_as_choices())
    tracks = MultipleFileField(_('Tracks'),
            [wtforms.validators.Required()],
            description= _("Use CTRL and/or SHIFT to select multiple items"),
            id="wmd-input")

class DogmaTracksGlobal(XXDogmaTracksGlobal):
    composers = TextField(
        u'Compositeur(s) pour tous les titres',
        [tag_length_validator],
        description=u"Séparez les noms par des virgules.")
    authors = TextField(
        u'Auteur(s) pour tous les titres',
        [tag_length_validator],
        description=u"Séparez les noms par des virgules.")
    tags = TextField(
        u'Tags pour tous les titres',
        [tag_length_validator],
        description=u"Séparez les noms par des virgules. Les tags des chansons seront ajoutés aux tags globaux.")
    license = wtforms.SelectField(
        u'Licence pour tous les titres',
        [wtforms.validators.Optional()],
        choices=licenses_as_choices())
    tracks = MultipleFileField('Titres',
            [wtforms.validators.Required()],
            description= u"Utilisez CTRL et/ou SHIFT pour sélectionner plusieurs éléments",
            id="wmd-input")

class XXBandForm(wtforms.Form):
    country_0 = wtforms.SelectField(
        _('Country'),
        [wtforms.validators.Optional()],
        description=_("Click the checkbox bellow if it's an internationnal band"),
        choices=countries_list())
    internationnal_0 = wtforms.BooleanField(_('Internationnal band'))
    Location = wtforms.FormField(LocationForm)
    band_name = TextField(
        _('Name *'),
        [wtforms.validators.Required()]
        )
    band_picture = wtforms.FileField(
                     _('Band picture'),
                     description=_("You can use format *.jpeg or *.jpg filetypes")
                   )
    band_description = TextAreaField(
        _('Description of the band'),
        [wtforms.validators.Required()],
        description=_("""You can use
                      <a href="http://daringfireball.net/projects/markdown/basics">
                      Markdown</a> for formatting."""),
        id="wmd-input_0"
        )
    band_since = DatePickerField(
            _('This band exists since :'),
            [wtforms.validators.Required()],
            description = _("date format YYYY-MM-DD"),
            pattern = "(19|20)\d\d-(0[1-9]|[1-9]|1[012])-(0[1-9]|[1-9]|[12][0-9]|3[01])"
            )
    
class BandForm(XXBandForm):
    country_0 = wtforms.SelectField(u'Pays',
        [wtforms.validators.Optional()],
        description=u"Cochez la case pour indiquer un groupe international.",
        choices=countries_list())
    internationnal_0 = wtforms.BooleanField(u'Groupe international')
    Location = wtforms.FormField(LocationForm)
    band_name = TextField(
        u'Nom *',
        [wtforms.validators.Required()]
        )
    band_picture = wtforms.FileField(
                     u'image du groupe',
                     description=u"Uniquement en format de fichier *.jpeg ou *.jpg"
                   )
    band_description = TextAreaField(
        u'Description du groupe',
        [wtforms.validators.Required()],
        description=DogmaUtilMKBOOK(),
         id="wmd-input_0"
        )
    band_since = DatePickerField(
            u'Ce groupe existe depuis :',
            [wtforms.validators.Required()],
            description = u"date au format YYYY-MM-DD",
            pattern = "(19|20)\d\d-(0[1-9]|[1-9]|1[012])-(0[1-9]|[1-9]|[12][0-9]|3[01])"
            )
   
class XXBandSelectForm(wtforms.Form):
    band_select = QuerySelectField(
        _('Bands'),
        allow_blank=True, blank_text=_('-- Select --'), get_label='name')

class BandSelectForm(XXBandSelectForm):
    band_select = QuerySelectField(
        u'Groupe',
        allow_blank=True, blank_text= u"-- Sélection --", get_label='name')

class XXMemberForm(wtforms.Form):
    member_username_0 = TextField(
        _('User name *'),
        [wtforms.validators.Required()]
        )
    member_real_name_0 =  TextField(
        _('Real name')
        )
    country_0 = wtforms.SelectField(
        _('Country'),
        [wtforms.validators.Optional()],
        description=_("Click the checkbox bellow if it's an internationnal band"),
        choices=countries_list())
    Location = wtforms.FormField(LocationForm)

    member_picture_0 = wtforms.FileField(_('Picture'))
    member_description_0 =  wtforms.TextAreaField(
        _('Bio'),
        description=_("""You can use
                      <a href="http://daringfireball.net/projects/markdown/basics">
                      Markdown</a> for formatting."""),
        id="wmd-input_0"
        )
    member_since_0 = DatePickerField(_('Member Since'),
            [wtforms.validators.Required()],
            description = _("date format YYYY-MM-DD"),
            quick_date = _("Member since the begining of the band"),
            pattern = "(19|20)\d\d-(0[1-9]|[1-9]|1[012])-(0[1-9]|[1-9]|[12][0-9]|3[01])"
            )
    member_former_0 = wtforms.BooleanField(_('Former member'))
    member_until_0 = DatePickerField(_('Member until'),
                     description = _("date format YYYY-MM-DD"),
                     pattern = "(19|20)\d\d-(0[1-9]|[1-9]|1[012])-(0[1-9]|[1-9]|[12][0-9]|3[01])"
                    )
    member_main = wtforms.BooleanField(_('Permanent member'),
            description=_("Permanent members are listed as band members, others are listed as colaborators"),
            default = True)
        
class MemberForm(XXMemberForm):
    member_username_0 = TextField(
        u'Pseudonyme *',
        [wtforms.validators.Required()]
        )
    member_real_name_0 =  TextField(
        u'Nom et prénom'
        )
    country_0 = wtforms.SelectField(
        u'Pays',
        [wtforms.validators.Optional()],
        description=u"Cocher la case pour indiquer un groupe international",
        choices=countries_list())
    Location = wtforms.FormField(LocationForm)

    member_picture_0 = wtforms.FileField(u'image')
    member_description_0 =  wtforms.TextAreaField(
        u'Biographie',
        description=DogmaUtilMKBOOK(),
        id="wmd-input_0"
        )
    member_since_0 = DatePickerField(u'simple membre',
            [wtforms.validators.Required()],
            description = u"date au format YYYY-MM-DD",
            quick_date = u"Membre au commencement du groupe",
            pattern = "(19|20)\d\d-(0[1-9]|[1-9]|1[012])-(0[1-9]|[1-9]|[12][0-9]|3[01])"
            )
    member_former_0 = wtforms.BooleanField('Ancien membre')
    member_until_0 = DatePickerField("Membre jusqu'au ",
                     description = "date au format YYYY-MM-DD",
                     pattern = "(19|20)\d\d-(0[1-9]|[1-9]|1[012])-(0[1-9]|[1-9]|[12][0-9]|3[01])"
                    )
    member_main = wtforms.BooleanField(u'Membre permanent',
            description=
	u"Les membres permanents sont répertoriés en tant que membre du groupe, les autres sont considérés comme colaborators",
            default = True)
        
class XXAlbumForm(wtforms.Form):
    release_date = DatePickerField(_('Release date of this album *'),
            [wtforms.validators.Required()],
            custom_class=_("album_release")
            )
    collection_title = TextField(
        _('Album Title'),
        [wtforms.validators.Required(),
        wtforms.validators.Length(min=0, max=500)])
    album_picture = wtforms.FileField(
                    _('Album cover'),
                    description = _("You can only upload *.jpg. An album cover must be a square")
                    )
    collection_description = wtforms.TextAreaField(
        _('Description of this Album'),
        description=_("""You can use
                      <a href="http://daringfireball.net/projects/markdown/basics">
                      Markdown</a> for formatting."""),
                      id="wmd-input_0"
                     )

class AlbumForm(XXAlbumForm):
    release_date = DatePickerField(u'Date de sortie de cet album *',
            [wtforms.validators.Required()],
            custom_class=u"album_release"
            )
    collection_title = TextField(
        u"Titre de l'album",
        [wtforms.validators.Required(),
        wtforms.validators.Length(min=0, max=500)])
    album_picture = wtforms.FileField(
                    u"Image de couverture",
                    description = u"Uniquement en format de fichier *.jpeg ou *.jpg et un format de page carré"
                    )
    collection_description = wtforms.TextAreaField(
        u'Description de cet album',
        description=DogmaUtilMKBOOK(),
		id="wmd-input_0"
                     )

class MemberRolesInput(object):
    def __call__(self, field, **kwargs):
        if field.millis_until:
            until = 'data-until="'+str(field.millis_until)+'"'
        else:
            until = u''

        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        id_field_name = 'member_'+str(field.count)
        html = [u'<div class="album_member" data-since="'+str(field.millis_since)+'"'+str(until)+'>\
             <input %s />' % html_params(name=field.name, type="text", **kwargs)\
            +'<input %s />' % html_params( name=id_field_name, value=field.member_id, type="hidden")+ '</div>']
        return HTMLString(u''.join(html))

class MemberRolesField(wtforms.FileField):
    widget = MemberRolesInput()

    def __init__(self,label=None, validators=None, count=None,iterable_value = u'', millis_since=u'',\
            millis_until=u'', member_id=u'',  **kwargs):
        super(MemberRolesField, self).__init__(label, validators, **kwargs)
        self.millis_until = millis_until
        self.millis_since = millis_since
        self.member_id = member_id
        self.count= count
        self.iterable_value = iterable_value

class XXAlbumMembersforms(wtforms.Form):
    roles = MemberRolesField(_('Instrument played * by '),
            [wtforms.validators.Required()],
            count = 0,
            description=_(
              "Separate roles by commas.")
            )

class AlbumMembersforms(XXAlbumMembersforms):
    roles = MemberRolesField(u'Instrument joué* par',
            [wtforms.validators.Required()],
            count = 0,
            description=u"Séparez les interprètes par des virgules."
            )

