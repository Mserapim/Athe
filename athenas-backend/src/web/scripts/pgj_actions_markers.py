#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pygeocoder import Geocoder
from rh.models import Comarca as County
from web.models import CountyMarker, MapMarker, Map, Area, ContentArea


def get_site(slug):
    return Area.objects.get(active=True, parent__isnull=True, slug=slug)


def get_counties():
    return County.objects.filter(circunscricao__isnull=False).order_by("nome")


def create_map(site_slug):
    print("======================Creating Map==========================")
    center, created = MapMarker.objects.get_or_create(latitude=-9.0, longitude=-48.3)
    _map, created = Map.objects.get_or_create(
        title="Mapa das atuações do MPE-TO", center=center
    )
    site = get_site(site_slug)
    ContentArea.objects.get_or_create(area=site, content=_map.content_ptr)
    print(
        "Map created at site: %s => %s"
        % (
            site,
            ContentArea.objects.filter(area=site, content=_map.content_ptr).exists(),
        )
    )

    return _map


def clear_markers():
    m = create_map()
    m.markers.clear()
    CountyMarker.objects.all().delete()


def create_markers(site_slug):
    print("=====================Creating markers======================")
    m = create_map(site_slug)
    counties = get_counties()

    for county in counties:
        print("County: %s" % county.nome)
        rs = Geocoder.geocode("%s, Tocantins, Brasil" % county.nome)
        print("Coordinates: %s, %s" % rs.coordinates)

        print("Creating marker")
        lat, lng = rs.coordinates
        marker, created = MapMarker.objects.get_or_create(latitude=lat, longitude=lng)

        print("Relating county and marker")
        cm, created = CountyMarker.objects.get_or_create(marker=marker, county=county)
        print("Creating CountyMarker: %s" % cm)

        if not m.markers.filter(latitude=lat, longitude=lng):
            print("Adding marker: %s to map" % marker)
            m.markers.add(marker)
        else:
            print("Marker %s already exists on map" % marker)
        print("------------------------------------------------")


def main(site_slug="portal"):
    create_markers(site_slug)
