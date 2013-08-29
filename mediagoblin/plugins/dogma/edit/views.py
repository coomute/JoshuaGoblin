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

import os
import logging

_log = logging.getLogger(__name__)

from datetime import datetime
import time

from werkzeug.exceptions import Forbidden
from werkzeug.utils import secure_filename

from mediagoblin import messages
from mediagoblin import mg_globals

from mediagoblin.edit import forms
from mediagoblin.plugins.dogma import forms as dogma_forms
from mediagoblin.plugins.dogma_lib.lib import (save_pic, list_as_string, save_member_specific_role, get_albums, may_edit_object,
        convert_to_list_of_dicts, save_member_if_new, store_keywords)
from mediagoblin.decorators import (require_active_login, active_user_from_url,
     get_media_entry_by_id,
     user_may_alter_collection, get_user_collection)
from mediagoblin.tools.response import render_to_response, \
    redirect, redirect_obj
from mediagoblin.tools.translate import pass_to_ugettext as _
from mediagoblin.tools.text import (
    convert_to_tag_list_of_dicts, media_tags_as_string)
from mediagoblin.tools.url import slugify
from mediagoblin.db.util import check_media_slug_used, check_collection_slug_used
from mediagoblin.plugins.dogma.models import (DogmaBandDB, BandMemberRelationship) 
from mediagoblin.db.models import (Collection)
from mediagoblin.messages import add_message, SUCCESS

import mimetypes

@require_active_login
def editBand(request):

    #GET MEMBER
    band = DogmaBandDB.query.filter_by(
        id = request.matchdict['band_id']).first()
    if not may_edit_object(request, band, 'creator'):
        raise Forbidden("User may not edit this member")

    i18n_band = False
    if band.place == 'int_band':
        i18n_band = True

    defaults = dict(
            country_0 = band.country,
            internationnal_0 = i18n_band,
            location_0 = band.place,
            place_0 = band.place,
            band_name = band.name,
            band_description = band.description,
            latitude_0 = band.latitude,
            longitude_0 = band.longitude,
            band_since = band.since,
        )



    form = dogma_forms.BandForm(request.form, **defaults)
    #The creation date of the date is turned into milliseconds so it can be used by template's calendar
    form.band_since.millis = str(int(time.mktime(band.since.timetuple())*1000))

    image_path = os.path.abspath("mediagoblin/plugins/dogma/static/images/uploaded/band_photos")
    try:
        open(image_path+'/'+str(band.id)+".jpeg")
        image_url = request.staticdirect('images/uploaded/band_photos/thumbs/'+str(band.id)+'_th.jpeg', 'coreplugin_dogma')
    except:
        image_url = False

    if request.method == 'POST' and form.validate():
        band.name = form.band_name.data
        band.description = form.band_description.data
        band.since = form.band_since.data
        band.latitude = request.form.get("latitude_0")
        band.longitude = request.form.get("longitude_0")
        band.country = request.form.get("country_0")
        band.place = request.form.get("location_0")
        band.save()





        save_pic(request,'band_picture',image_path, band.id)

        add_message(request, SUCCESS, _('Band successfully modified !'))
        return redirect(request, "mediagoblin.plugins.dogma.dashboard")

    return render_to_response(
        request,
        'dogma/edit/edit_band.html',
        {
            'image_url': image_url,
            'form' : form,
            'band' : band
         })
@require_active_login
def editMember(request):

    #GET MEMBER
    band = DogmaBandDB.query.filter_by(
        id = request.matchdict['band_id']).first()
    member = BandMemberRelationship.query.filter_by(
        member_id = request.matchdict['member_id'], band_id = band.id).first()
    member_global = member.member_global
    if not may_edit_object(request, member_global, 'creator'):
        raise Forbidden("User may not edit this member")

    defaults = dict(
        member_username_0=member_global.username,
        member_real_name_0=member_global.real_name,
        member_description_0=member_global.description,
        member_since_0 = member.since,
        member_until_0 = member.until,
        member_former_0 = member.former,
        member_main = member.main,
        )

    #The creation date of the date is turned into milliseconds so it can be used by template's calendar
    band.millis = int(time.mktime(band.since.timetuple())*1000)


    form = dogma_forms.MemberForm(request.form, **defaults)
    form_extra = dogma_forms.MemberEditExtras(request.form, **defaults)
    #Add the millisecond attribute to the input so it can be used by the JS
    #it needs to be int to be in millis then  turned into str for the WTForm widget
    form.member_since_0.millis = str(int(time.mktime(member.since.timetuple())*1000))
    if member.until:
        form.member_until_0.millis = str(int(time.mktime(member.until.timetuple())*1000))

    if request.method == 'POST' and form.validate():
        member_global.username= form.member_username_0.data
        member_global.slug = slugify(member_global.username)
        member_global.real_name= form.member_real_name_0.data
        member_global.description= form.member_description_0.data
        member_global.latitude= request.form.get('member_latitude_0')
        member_global.longitude= request.form.get('member_longitude_0')
        member_global.place= request.form.get('member_place_0')
        member_global.country= request.form.get('member_country_0')
        member_global.save()

        member.since = form.member_since_0.data
        member.until = form.member_until_0.data
        member.former = form.member_former_0.data
        member.main =  form_extra.member_main.data
        member.save()


        add_message(request, SUCCESS, _('Member successfully modified !'))
        return redirect(request, "mediagoblin.plugins.dogma.dashboard")

    return render_to_response(
        request,
        'dogma/edit/edit_member.html',
        {
            'form' : form,
            'form_extra' : form_extra,
            'member_global' : member_global,
            'member' : member,
            'band' : band
         })
@require_active_login
def editAlbum(request):

    band = DogmaBandDB.query.filter_by(
        id = request.matchdict['band_id']).first()
    #GET COLLECTION
    album_id = request.matchdict['album_id']
    album = Collection.query.filter_by(
        id = album_id ).first()
    #CHECK RIGHTS
    if not may_edit_object(request, album, 'creator'):
        raise Forbidden("User may not edit this member")
    #Check if this collection is an album
    if not album.get_album:
        raise Forbidden("This is not an album !")

    defaults = dict(
            collection_title = album.title,
            collection_description = album.description,
            release_date = album.get_album.release_date
        )
    key = 0

    #The creation date of the date is turned into milliseconds so it can be used by template's calendar
    band.millis = int(time.mktime(band.since.timetuple())*1000)

    #Test if there is an album cover
    image_path = os.path.abspath("mediagoblin/plugins/dogma/static/images/uploaded/album_covers")
    try:
        open(image_path+'/'+str(album.id)+".jpeg")
        image_url = request.staticdirect('images/uploaded/album_covers/thumbs/'+str(album.id)+'_th.jpeg', 'coreplugin_dogma')
    except:
        image_url = False


    form = dogma_forms.AlbumForm(request.form, **defaults)
    roles_form_list = list()
    for member  in band.members:
        #skip none main members
        if not member.main:
            continue
        #filter the kw with type and album ID (you don't want roles from another album)
        kw_params =  dict(type='role', album=album.id)
        keywords = list_as_string(member.member_global.get_keywords,'data', kw_params)
        #The name of the field changes later. Use the unmodified name 'roles' for **defaults.
        defaults['roles']= list_as_string(member.member_global.get_keywords,'data', kw_params)
        roles_form = dogma_forms.AlbumMembersforms(request.form, **defaults) 
        member_roles_form =roles_form.roles
        #adding the member's name to the field
        member_roles_form.label.text =  member_roles_form.label.text + member.member_global.username
        member_roles_form.name =  member_roles_form.name + '_'+str(key) 
        member_roles_form.count = key
        #Add the millisecond attribute to the input so it can be used by the JS
        #it needs to be int to be in millis then  turned into str for the WTForm widget
        member_roles_form.millis_since = int(time.mktime(member.since.timetuple())*1000)
        if member.until:
            member_roles_form.millis_until = int(time.mktime(member.until.timetuple())*1000)
        else:
            member_roles_form.millis_until = False
        roles_form_list.append(roles_form)
        member_roles_form.member_id = member.id
        key = key+1
    #creating the millis for the release date
    form.release_date.millis = str(int(time.mktime(defaults['release_date'].timetuple())*1000))
    if request.method == 'POST' and form.validate():
        save_pic(request,'album_picture', image_path, album_id, True)

        album.title = form.collection_title.data
        album.description = form.collection_description.data
        album.get_album.release_date = form.release_date.data
        album.save()

        #ROLES
        role_index = 0
        #loop the members and save them all
        while not request.form.get('roles_'+str(role_index)) == None:
            print 'lknljn'
            # store roles as keywords using the tags tools
            store_keywords(request.form.get("roles_"+str(role_index)), False, 
                    request.form.get("member_"+str(role_index)), album.id, False, 'role')
            role_index += 1

        add_message(request, SUCCESS, _('Album successfully modified !'))
        return redirect(request, "mediagoblin.plugins.dogma.dashboard")


    return render_to_response(
        request,
        'dogma/edit/edit_album.html',
        {
            'image_url': image_url,
            'form' : form,
            'roles_form_list' : roles_form_list,
            'band' : band,
            'album': album
         })

@get_media_entry_by_id
@require_active_login
def editTrack(request, media):
    if not may_edit_object(request, media, 'uploader'):
        raise Forbidden("User may not edit this media")

    defaults = dict(
        title_0=media.title,
        description_0=media.description,
        tags_0=media_tags_as_string(media.tags),
        license_0=media.license,
        )
    form = dogma_forms.DogmaTracks(
        request.form,
        **defaults)
    keywords = media.get_keywords
    if request.method == 'POST' and form.validate():
        #the anti-member-duplicates dict
        existing_members ={}

        #save new roles for each band that has this track (as a collaborator)
        bands = list()
        band_no = 0

        #get all possible bands for all possible albums
        for album in get_albums(media):
            bands.append(album.get_band_relationship[band_no].band)
            band_no += 1

        #store the roles for each bands
        for band in bands:
            #Check if authors or composers field has been changed and process the data if so
            specific_roles = set(["authors", "composers"])
            for role in specific_roles:
                if request.form.get(role+'_0'):
                        existing_members = save_member_specific_role(role, media, band,
                                existing_members, request.form, 0)

            #extra members
            p_key = 0
            pattern = 'No'+str(p_key)+'_0'
            while request.form.get('performer'+pattern):

                #Use this function to get a name and a slug (can be used with a comma separated list)
                dics_list = convert_to_list_of_dicts(request.form.get('performer'+pattern), "username")

                for member_dict in dics_list:
                    #passe the new member alongside to a list of already created users to avoid duplicates
                    existing_members = save_member_if_new(member_dict, existing_members, band)
                    #get this id out of existing members  with the member's slug as a key
                    member_id = existing_members[member_dict["slug"]]
                    #store keywords
                    store_keywords(request.form.get("performer_roles"+pattern), band.id, 
                            member_id, False, media.id, 'role')
                p_key+=1
                pattern = 'No'+str(p_key)+'_0'

        #Delete what you have to among composers/authors or roles
        for author in media.get_authors:
            if int(request.form.get('rm_author_'+str(author.id)) or 0) == author.id:
                author.delete()
        for composer  in media.get_composers:
            if int(request.form.get('rm_composer_'+str(composer.id)) or 0) == composer.id:
                composer.delete()
        for keyword  in media.get_keywords:
            if int(request.form.get('rm_role_'+str(keyword.id)) or 0) == keyword.id:
                keyword.delete()

        if form.title_0.data:
            media.title = form.title_0.data
            media.slug = slugify(media.title)
        media.description = form.description_0.data
        media.tags = convert_to_tag_list_of_dicts(
                               form.tags_0.data)

        media.license = unicode(form.license_0.data) or None
        media.save()

        add_message(request, SUCCESS, _('Track successfully modified !'))
        return redirect_obj(request, media)

    if request.user.is_admin \
            and media.uploader != request.user.id \
            and request.method != 'POST':
        messages.add_message(
            request, messages.WARNING,
            _("You are editing another user's media. Proceed with caution."))

    return render_to_response(
        request,
        'dogma/edit/edit_track.html',
        {'media': media,
         'tracks_form': form,
         'keywords': keywords
         })
