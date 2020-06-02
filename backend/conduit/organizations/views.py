# coding: utf-8

import datetime as dt

from flask import Blueprint, jsonify
from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import current_user, jwt_required, jwt_optional
from marshmallow import fields
from sqlalchemy.exc import IntegrityError

from conduit.database import db
from conduit.exceptions import InvalidUsage
from .models import Organization
from conduit.user.models import User
from conduit.profile.models import UserProfile
from conduit.articles.models import Article
from conduit.tags.models import Tags

from .serializers import (organization_schema, organizations_schema)
from conduit.profile.serializers import (profile_schema, profile_schemas)
from conduit.articles.serializers import (org_article_schema, org_articles_schema)

blueprint = Blueprint('organizations', __name__)


###############
# Organizations
###############


@blueprint.route('/api/organizations', methods=('POST',))
@jwt_required
@use_kwargs(organization_schema)
@marshal_with(organization_schema)
def make_organization(name, description, slug, **kwargs):
    try:
        organization = Organization(name=name, description=description, slug=slug)
        profile = current_user.profile
        organization.add_moderator(profile)
        organization.save()
    except IntegrityError:
        db.session.rollback()
        raise InvalidUsage.slug_already_exists()

    return organization


@blueprint.route('/api/organizations/<slug>', methods=('GET',))
@jwt_optional
@marshal_with(organization_schema)
def get_organization(slug):
    organization = Organization.query.filter_by(slug=slug).first()
    if not organization:
        raise InvalidUsage.organization_not_found()

    return organization


@blueprint.route('/api/organizations/<slug>', methods=('PUT',))
@jwt_required
@use_kwargs(organization_schema)
@marshal_with(organization_schema)
def update_organization(slug, old_slug, **kwargs):
    organization = Organization.query.filter_by(slug=old_slug).first()
    if not organization:
        raise InvalidUsage.organization_not_found()
    organization.update_slug(slug)
    organization.update(**kwargs)
    organization.save()

    return organization


@blueprint.route('/api/organizations/<slug>', methods=('DELETE',))
@jwt_required
def delete_organization(slug):
    organization = Organization.query.filter_by(slug=slug).first()
    organization.delete()

    return '', 200


@blueprint.route('/api/organizations/<slug>/follow', methods=('POST',))
@jwt_required
@marshal_with(organization_schema)
def follow_organization(slug):
    profile = current_user.profile
    organization = Organization.query.filter_by(slug=slug).first()
    if not organization:
        raise InvalidUsage.organization_not_found()
    organization.add_member(profile)
    organization.save()

    return organization


@blueprint.route('/api/organizations/<slug>/follow', methods=('DELETE',))
@jwt_required
@marshal_with(organization_schema)
def unfollow_organization(slug):
    profile = current_user.profile
    organization = Organization.query.filter_by(slug=slug).first()
    if not organization:
        raise InvalidUsage.organization_not_found()
    organization.remove_member(profile)
    organization.save()

    return organization


@blueprint.route('/api/organizations/<slug>/members', methods=('GET',))
@jwt_required
@marshal_with(organization_schema)
def show_all_members_mods(slug):
    organization = Organization.query.filter_by(slug=slug).first()
    if not organization:
        raise InvalidUsage.organization_not_found()
    
    return organization


@blueprint.route('/api/organizations/<slug>/members', methods=('POST',))
@jwt_required
@use_kwargs(profile_schema)
@marshal_with(profile_schema)
def promote_member(slug, username, **kwargs):
    profile = current_user.profile
    organization = Organization.query.filter_by(slug=slug).first()
    user = User.query.filter_by(username=username).first()
    if organization.moderator(profile):
        organization.promote(user.profile)
    organization.save()

    return user.profile


@blueprint.route('/api/organizations/<slug>/members', methods=('DELETE',))
@jwt_required
@use_kwargs(profile_schema)
@marshal_with(profile_schema)
def remove_member(slug, username, **kwargs):
    profile = current_user.profile
    organization = Organization.query.filter_by(slug=slug).first()
    user = User.query.filter_by(username=username).first()
    if organization.moderator(profile):
        organization.remove_member(user.profile)
    organization.save()

    return '', 200


@blueprint.route('/api/organization/<org_slug>/articles', methods=('POST',))
@jwt_required
@use_kwargs(org_article_schema)
@marshal_with(org_article_schema)
def submit_article_for_review(body, title, description, 
                            org_slug, tagList=None):
    profile = current_user.profile
    organization = Organization.query.filter_by(slug=org_slug).first()
    article = Article(title=title, description=description, body=body, 
                      author=current_user.profile)

    if tagList is not None:
        for tag in tagList:
            mtag = Tags.query.filter_by(tagname=tag).first()
            if not mtag:
                mtag = Tags(tag)
                mtag.save()
            article.add_tag(mtag)
    
    article.needsReview = True
    article.save()
    organization.request_review(article)
    organization.save()
    
    return article


@blueprint.route('/api/organization/<org_slug>/articles', methods=('DELETE',))
@jwt_required
@use_kwargs(org_article_schema)
@marshal_with(org_article_schema)
def publish_article(title, org_slug, **kwargs):
    organization = Organization.query.filter_by(slug=org_slug).first()
    article = Article.query.filter_by(title=title).first()

    if article in organization.pending_articles:
        article.needsReview = False
        article.org_articles.append(article)
        organization.remove_review_status(article)
        
        article.save()
        organization.save()

    return article

@blueprint.route('/api/organization/<org_slug>/articles', methods=('GET',))
@jwt_required
@use_kwargs(org_articles_schema)
@marshal_with(org_articles_schema)
def get_org(title, org_slug, **kwargs):
    organization = Organization.query.filter_by(slug=org_slug).first()
    article = Article.query.filter_by(title=title).first()



    return organization
