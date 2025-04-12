Ext.ns('toolkit.web.intranet');


toolkit.web.intranet.cleanup = function(val)
{
    val = toolkit.util.replaceAll(val, '\\', '');
    val = toolkit.util.replaceAll(val, '¿', '');
    return val;
}

toolkit.web.intranet.createStore = function(config)
{
    var defaultConfig = {
        autoLoad: true,
        root: 'list',
        remoteSort: true,
        totalProperty: 'total',
        baseParams: {start: 0, limit: 20},
    };

    config = Ext.apply(defaultConfig, config);

    return new Ext.data.JsonStore(config);
}

toolkit.web.intranet.applyClickToShowDetails = function(selector, store)
{

    var items = Ext.select(selector);
    items.on('click', function(ev, target) {
        var parent = new Ext.Element(target).parent();
        var record = store.getAt( items.indexOf(parent) );
        if(record)
        {
            var loading = new Ext.LoadMask(toolkit.Application.tabspace.getActiveTab().getEl(), {msg: 'Aguarde...'});
            loading.show();
            Ext.Ajax.request({
                url: action('intranet/get_post/json'),
                method: 'GET',
                params: {
                    areas__parent__slug: 'intranet',
                    id: record.get('id'),
                    'image-width': 350,
                    'image-cut-mode': 'width',
                    'image-sizes': 'square|35'
                },
                success: function(response)
                {
                    var obj = Ext.decode(response.responseText);
                    toolkit.web.intranet.showDetails(obj);
                    loading.hide();
                }
            });
        }
    });
}

toolkit.web.intranet.showDetails = function(params)
{
    var template = new Ext.XTemplate(
        '<div class="intranet intranet-detail">',
            '<h1>{[this.cleanup(values.title)]}</h1>',
            '<tpl if="front_image_url">',
                '<div class="image-box rounded">',
                    '<div class="focus-image">',
                        '<img src="{front_image_url}"/>',
                        '<p>{[this.cleanup(values.front_image_title)]}</p>',
                    '</div>',
                    '<tpl if="more_images">',
                        '<ul class="thumb-list">',
                            '<tpl for="images">',
                                '<li <tpl if="is_last">class="omega"</tpl>>',
                                    '<img src="{url_size_35}" ext:qtip="{title}"/>',
                                    '<div class="hide">',
                                        '<img src="{url}"/>',
                                        '<p>{[this.cleanup(values.title)]}</p>',
                                    '</div>',
                                '</li>',
                            '</tpl>',
                        '</ul>',
                    '</tpl>',
                '</div>',
            '</tpl>',
            '<div class="text">{[this.cleanup(values.text)]}</div>',
            '<tpl if="has_files">',
                '<div class="files rounded">',
                    '<span>Downloads</span>',
                    '<ul>',
                        '<tpl for="files">',
                            '<li><a href="{url}">{[this.cleanup(values.title)]}</a></li>',
                        '</tpl>',
                    '</ul>',
                '</div>',
            '</tpl>',
        '</div>',
        { cleanup: toolkit.web.intranet.cleanup }
    );

    new Ext.Window({
        modal: true,
        frame: true,
        items: [
            {
                //autoHeight: true,
                border: false,
                autoScroll: true,
                padding: 10,
                height: 550,
                width: 650,
                html: template.apply(params)
            }
        ],
        listeners: {
            afterrender: function(cmp)
            {
                var els = Ext.select('.intranet-detail .focus-image img');
                if (els.getCount() > 0)
                {
                    els.first().dom.onload = function()
                    {
                        var focusP = Ext.select('.intranet-detail .focus-image p').first();
                        focusP.set({style: 'width:'+this.width+'px'});
                        if(this.alt)
                            focusP.update(this.alt);
                    }

                    Ext.select('.intranet-detail .thumb-list li', true).on('click', function(ev, target){
                        var thumb = new Ext.Element(target).parent('li'),
                            hideImg = Ext.select('.hide img', true, thumb.dom).first(),
                            hideP = Ext.select('.hide p', true, thumb.dom).first(),
                            focusImg = Ext.select('.intranet-detail .focus-image img').first();

                        focusImg.set({src: hideImg.getAttribute('src'), alt: hideP.dom.innerHTML});
                    });
                }
            }
        }
    }).show();
}

toolkit.web.intranet.App = Ext.extend(toolkit.widget.TabPanel, {
    constructor: function(opts)
    {

        if(opts.employeeRemoved)
        {
            Ext.getCmp('btn-athenas-menu').hide();

            Ext._create('Ext.Window', {
                title: 'AVISO',
                modal: true,
                frame: true,
                resizable: false,
                maxHeight: 450,
                minWidth: 350,
                maxWidth: 660,
                data: opts.employeeRemoved,
                tpl: Ext._create('Ext.XTemplate', [
                    '<tpl for=".">',
                        '<div class="intranet-lite">',
                            '<p class="warning">{name}, você está afastado(a).<br/>Motivo, <b>{reason}</b>.<br/>Devido ao afastamento você terá acesso limitado.</p>',
                        '</div>',
                    '</tpl>'
                ])
            }).show();
        }

        // if(opts.hasToVote)
        // {
        //     console.log('Has poll(s) to vote.');
        //     new toolkit.common.poll.VotePolls();
        // }

        this.menu = new toolkit.web.intranet.Menu();
        this.news = new toolkit.web.intranet.News();
        this.birthdays = new toolkit.web.intranet.Birthdays();
        this.featured = new toolkit.web.intranet.Featured();
        this.todayMPE = new toolkit.web.intranet.TodayMPE();

        this.featured.stopSlider();

        toolkit.web.intranet.App.superclass.constructor.call(this, {
            id: 'intranet-app',
            title: 'Intranet',
            closable: true,
            autoScroll: true,
            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [
                {
                    width: 200,
                    minWidth: 200,
                    maxWidth: 200,
                    padding: '7px 0 7px 7px',
                    border: false,
                    layout: {
                        type: 'vbox',
                        align: 'stretch'
                    },
                    items: [
                        {
                            height: 25,
                            xtype: 'compositefield',
                            items: [
                                {
                                    xtype: 'button',
                                    text: 'limpar',
                                    height: 25,
                                    width: 41,
                                    //width: 45,
                                    tyle: {
                                        border: 'none',
                                        padding: '2px'
                                    },
                                    handler: function()
                                    {
                                        Ext.getCmp('intranet-search-field').setValue('');
                                        this.news.getStore().setBaseParam('search_by', '');
                                        this.news.getStore().load();

                                        this.featured.getStore().setBaseParam('search_by', '');
                                        this.featured.getStore().load();

                                        this.todayMPE.getStore().setBaseParam('search_by', '');
                                        this.todayMPE.getStore().load();
                                    },
                                    scope: this
                                },
                                {
                                    id: 'intranet-search-field',
                                    xtype: 'textfield',
                                    emptyText: 'Pesquisar',
                                    enableKeyEvents: true,
                                    height: 23,
                                    width: 145,
                                    //border: false,
                                    listeners: {
                                        keydown: function(field, event)
                                        {
                                            if(event.getKey() == event.ENTER)
                                            {
                                                this.news.getStore().setBaseParam('search_by', field.getValue());
                                                this.news.getStore().load();

                                                this.featured.getStore().setBaseParam('search_by', field.getValue());
                                                this.featured.getStore().load();

                                                this.todayMPE.getStore().setBaseParam('search_by', field.getValue());
                                                this.todayMPE.getStore().load();
                                            }
                                        },
                                        scope: this
                                    }
                                }
                            ]
                        },
                        this.menu,
                        this.birthdays
                    ]
                },
                {
                    flex: 1,
                    minWidth: 356,
                    border: false,
                    padding: 7,
                    layout: {
                        type: 'hbox',
                        align: 'stretch'
                    },
                    items: [
                        {
                            // id: 'news-box',
                            title: 'Informes',
                            minHeight: 500,
                            flex: 1,
                            autoScroll: true,
                            items: this.news,
                            tbar: [this.news.getComboAreas()],
                            bbar: this.news.getPaging()
                        },
                    ]
                },
                {
                    width: 430,
                    border: false,
                    padding: '7px 7px 7px 0',
                    layout: {
                        type: 'vbox',
                        align: 'stretch'
                    },
                    items: [
                        this.featured,
                        this.todayMPE
                    ]
                }
            ],
            listeners: {
                show: function()
                { this.featured.stopSlider(); },
                close: function()
                {
                    this.featured.stopSlider();
                    toolkit.Application.createFormFor('Intranet');
                },
                scope: this
            }
        });

        // toolkit.Application.tabspace.add(this);
        // toolkit.Application.tabspace.activate(this);
    }
});

// _TODEL_ Existe uma nova implementação para "Portal do servidor" no novo Dashboard.
toolkit.web.intranet.Menu = Ext.extend(Ext.Panel, {
    constructor: function()
    {
        toolkit.web.intranet.Menu.superclass.constructor.call(this, {
            title: 'Portal do servidor',
            minHeight: 250,
            height: 250,
            autoScroll: true,
            items: [this.getMenuItems()],
            style: {
                paddingTop: '7px'
            }
        });
    },

    getMenuItems: function()
    {
        if(!this._menuItems)
        {
            this._menuItems = new Ext.DataView({
                store: this.getStore(),
                itemSelector: '.list-item',
                emptyText: 'Sem itens para exibir.',
                tpl: new Ext.XTemplate(
                    '<div class="intranet intranet-menu">',
                        '<ul>',
                            '<tpl for=".">',
                                '<li><a href="{href}" target="{target}">{text}</a></li>',
                            '</tpl>',
                        '</ul>',
                    '</div>'
                )
            });
        }
        return this._menuItems;
    },

    getStore: function()
    {
        if(!this._store)
        {
            this._store = toolkit.web.intranet.createStore({
                fields: ['text', 'href', 'target'],
                url: action('intranet/get_menu/json')
            });
        }
        return this._store;
    }
});


toolkit.web.intranet.Birthdays = Ext.extend(Ext.Panel, {
    constructor: function()
    {
        toolkit.web.intranet.Menu.superclass.constructor.call(this, {
            title: 'Aniversários',
            minHeight: 228,
            autoScroll: true,
            flex: 1,
            style: {
                paddingTop: '7px'
            },
            items: [this.getBirthdays()]
        });
    },

    getBirthdays: function()
    {
        if(!this._birthdays)
        {
            this._birthdays = new Ext.DataView({
                store: this.getStore(),
                itemSelector: '.list-item',
                emptyText: 'Sem itens para exibir.',
                tpl: new Ext.XTemplate(
                    '<div class="intranet intranet-birthdates">',
                        '<ul>',
                            '<tpl for=".">',
                                '<li ext:qtip="Lotação: {department}">',
                                    '<tpl if="photo_url">',
                                        '<span class="image-box"><img src="{photo_url}"></span>',
                                    '</tpl>',
                                    '<span class="employee-info">{birthdate} - {name}</span>',
                                '</li>',
                            '</tpl>',
                        '</ul>',
                    '</div>'
                )
            });
        }
        return this._birthdays;
    },

    getStore: function()
    {
        if(!this._store)
        {
            this._store = toolkit.web.intranet.createStore({
                fields: ['name', 'href', 'department', 'photo_url', 'birthdate'],
                url: action('intranet/get_birthdays/json')
            });
        }
        return this._store;
    }
});


toolkit.web.intranet.News = Ext.extend(Ext.Panel, {
    _areasLoaded: false,

    constructor: function()
    {
        toolkit.web.intranet.News.superclass.constructor.call(this, {
            autoScroll: true,
            border: false
        });
    },

    getComboAreas: function()
    {
        if(!this._areas)
        {
            this._areas = new Ext.form.ComboBox({
                typeAhead: true,
                triggerAction: 'all',
                mode: 'local',
                store: this.getStoreAreas(),
                valueField: 'slug',
                displayField: 'name',
                emptyText: 'Categorias de publicação',
                listeners: {
                    select: function(combo, record)
                    {
                        var parameter = (record.get('slug')=='all') ? this.getAreasSlugList() : '[\''+ record.get('slug') +'\']'
                        this.getStore().setBaseParam('areas__slug__in', parameter);
                        this.getPaging().changePage(1);
                    },
                    scope: this
                }
            });
        }
        return this._areas
    },

    loadNews: function()
    {
        var loading = new Ext.LoadMask(this.ownerCt.getEl(), {msg: 'Aguarde...', removeMask: true});
        loading.show();
        this.add(this.getPosts(loading));
        this.doLayout();
    },

    getStoreAreas: function(callback) // Necessário para criar modal window de manuais
    {
        if(!this._storeAreas)
        {
            this._storeAreas = toolkit.web.intranet.createStore({
                fields: ['name', 'slug', 'parent'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('services/cms/areas/json')
                }),
                baseParams: {parent__slug: 'intranet', as_link: true},
                listeners: {
                    load: function(store)
                    {
                        store.insert(0, new Ext.data.Record({name: 'Todas as publicações', slug: 'all'}));
                        this._areasLoaded = true;
                        this.loadNews();

                        if(callback) // Necessário para criar modal window de manuais
                            callback(store);
                    },
                    scope: this
                }
            });
        }
        return this._storeAreas;
    },

    getPosts: function(loading)
    {
        if(!this._posts)
        {
            this._posts = new Ext.DataView({
                store: this.getStore(loading),
                itemSelector: '.list-item',
                emptyText: 'Sem itens para exibir.',
                tpl: new Ext.XTemplate(
                    '<tpl for=".">',
                        '<div class="list-item">',
                            '<tpl if="front_image_url">',
                                '<div class="image-box"><img src="{front_image_url}"></div>',
                            '</tpl>',
                            '<div class="date-area">',
                                '{date} - <tpl for="area">{name}</tpl>',
                            '</div>',
                            '<span>{[this.cleanup(values.title)]}</span>',
                            '<p>{[this.cleanup(values.abstract)]}</p>',
                        '</div>',
                    '</tpl>',
                    { cleanup: toolkit.web.intranet.cleanup }
                )
            });
        }
        return this._posts;
    },

    getStore: function(loading)
    {
        if(!this._store && this._areasLoaded)
        {
            this._store = toolkit.web.intranet.createStore({
                fields: ['id', 'title', 'slug', 'front_image_url', 'date', 'abstract', 'area', 'text'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('intranet/get_news/json')
                }),
                baseParams: {
                    areas__parent__slug: 'intranet',
                    areas__slug__in: this.getAreasSlugList(),
                    'image-width': 56,
                    'image-cut-mode': 'square',
                    start: 0,
                    limit: 10
                },
                listeners: {
                    load: function(store)
                    {
                        this.getPaging().bindStore(store);
                        var selector = '#' + this.ownerCt.id + ' .list-item';
                        toolkit.web.intranet.applyClickToShowDetails(selector, store);

                        if(loading)
                        { loading.hide(); }
                    },
                    scope: this
                }
            });
        }
        return this._store;
    },

    getPaging: function()
    {
        if(!this._paging)
        {
            this._paging = new Ext.PagingToolbar({
                store: this.getStore(),
                displayInfo: true,
                pageSize: 10,
                prependButtons: true
            })
        }
        return this._paging;
     },

    getAreasSlugList: function()
    {
        var slugs = [];
        this.getStoreAreas().each( function(record) {
            slugs[slugs.length] = "'"+record.get('slug')+"'";
        });
        return "["+slugs.join(',')+"]";
    }
});


toolkit.web.intranet.Featured = Ext.extend(Ext.Panel, {
    constructor: function()
    {
        toolkit.web.intranet.Featured.superclass.constructor.call(this, {
            title: 'Destaque',
            minHeight: 350,
            height: 350,
            autoScroll: true,
            items: [this.getFeaturedNews()],
            bbar: this.getPaging(),
            listeners: {
                render: function(cmp)
                { new Ext.LoadMask(this.getEl(), {msg: 'Aguarde...', store: this.getStore()}).show(); },
                scope: this
            }
        });
    },

    getFeaturedNews: function()
    {
        if(!this._featuredNews)
        {
            this._featuredNews = new Ext.DataView({
                store: this.getStore(),
                emptyText: 'Sem itens para exibir.',
                tpl: new Ext.XTemplate(
                    '<div class="intranet intranet-featured">',
                        '<ul class="tabs">',
                            '<tpl for="."><li id="slide-tab-{[xindex]}"<tpl if="xindex==1"> class="active"</tpl>>{[xindex]}</li></tpl>',
                        '</ul>',
                        '<ul class="focus">',
                            '<tpl for=".">',
                                '<li id="slide-{[xindex]}">',
                                    '<span class="image-box"><img src="{front_image_url}"></span>',
                                    '<span class="title">{[this.cleanup(values.title)]}</span>',
                                '</li>',
                            '</tpl>',
                        '</ul>',
                    '</div>',
                    { cleanup: toolkit.web.intranet.cleanup }
                )
            });
        }
        return this._featuredNews;
    },

    getStore: function()
    {
        if(!this._store)
        {
            this._store = toolkit.web.intranet.createStore({
                fields: ['id', 'title', 'slug', 'date', 'front_image_url', 'abstract', 'area', 'text'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('intranet/get_news/json')
                }),
                baseParams: {
                    areas__parent__slug: 'intranet',
                    areas__slug: 'destaque',
                    'image-width': 422,
                    'image-cut-mode': 'square',
                    reverse: true,
                    start: 0,
                    limit: 5
                },
                listeners: {
                    load: function(store)
                    {
                        if(store.getCount() > 0)
                        {
                            toolkit.web.intranet.applyClickToShowDetails('.intranet-featured .image-box', store);
                            this.activateSlider();
                        }
                        else
                            this.stopSlider();
                    },
                    scope: this
                }
            });
        }
        return this._store;
    },

    getPaging: function()
    {
        if(!this._paging)
        {
            this._paging = new Ext.PagingToolbar({
                store: this.getStore(),
                displayInfo: true,
                pageSize: 5,
                prependButtons: true
            })
        }
        return this._paging;
    },

    activateSlider: function()
    { this.prepareSlider().playSlider(); },

    prepareSlider: function(autoplay)
    {
        this.stopSlider();

        var pairs = {},
            tabs = Ext.select('.intranet-featured .tabs li', true),
            slides = Ext.select('.intranet-featured .focus li',  true),
            slideIndexes = slides.getCount() - 1,
            $this = this;

        tabs.each(function(tab, list, index) {
            var slide = slides.item(slideIndexes - index);
            pairs[tab.getAttribute('id')] = {
                tab: tab,
                slide: slide,
            };

            tab.dom.onclick = function(){
                var activeTab = Ext.select('.intranet-featured .tabs li.active', true).first(),
                    activeId = activeTab.dom.id,
                    active = pairs[activeId],
                    toChange = pairs[this.id];

                active.tab.removeClass('active');
                active.slide.set({style: 'z-index: 1;'});

                toChange.tab.addClass('active');
                toChange.slide.set({style: 'z-index: 5;'});
            }

            tab.on('mouseover', function() { $this.stopSlider(); });
            tab.on('mouseout', function() { $this.playSlider(); });
            slide.on('mouseover', function() { $this.stopSlider(); });
            slide.on('mouseout', function() { $this.playSlider(); });
        });

        this._pairs = pairs;

        return this;
    },

    playSlider: function()
    {
        var $this = this;
        toolkit.web.intranet.sliderInterval = setInterval(
            function()
            {
                var thereIs = Ext.getCmp('intranet-app');
                if(thereIs)
                {
                    var tabs = Ext.select('.intranet-featured .tabs li', true),
                        activeTab = Ext.select('.intranet-featured .tabs li.active', true).first(),
                        index = tabs.indexOf(activeTab.dom.id);

                    toChangeIndex = (index == tabs.getCount() - 1) ? 0 : index + 1;
                    tabs.item(toChangeIndex).dom.click();
                }
                else
                    $this.stopSlider();
            },
            2000
        );

        return this;
    },

    stopSlider: function()
    {
        clearInterval(toolkit.web.intranet.sliderInterval);
        return this;
    }
});


toolkit.web.intranet.TodayMPE = Ext.extend(Ext.Panel, {
    constructor: function()
    {
        toolkit.web.intranet.TodayMPE.superclass.constructor.call(this, {
            title: 'Ouça o Dia a Dia MPE',
            autoScroll: true,
            minHeight: 162,
            flex: 1,
            style: {
                paddingTop: '7px',
            },
            items: [this.getEpisodes()],
            bbar: this.getPaging(),
            listeners: {
                render: function(cmp)
                { new Ext.LoadMask(this.getEl(), {msg: 'Aguarde...', store: this.getStore()}).show(); },
                socpe: this
            }
        });
    },

    getEpisodes: function()
    {
        if(!this._episodes)
        {
            this._episodes = new Ext.DataView({
                store: this.getStore(),
                itemSelector: '.list-item',
                emptyText: 'Sem itens para exibir.',
                tpl: new Ext.XTemplate(
                    '<div class="intranet intranet-today-mpe">',
                        '<ul>',
                            '<tpl for=".">',
                                '<li><span>{[this.cleanup(values.title)]}</span></li>',
                            '</tpl>',
                        '</ul>',
                    '</div>',
                    { cleanup: toolkit.web.intranet.cleanup }
                )
            });
        }
        return this._episodes;
    },

    getStore: function()
    {
        if(!this._store)
        {
            this._store = toolkit.web.intranet.createStore({
                fields: ['id', 'title', 'slug', 'date', 'abstract', 'area', 'text'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('intranet/get_today_mpe_episodes/json')
                }),
                baseParams: {
                    areas__parent__slug: 'intranet',
                    areas__slug: 'dia-a-dia-mpe',
                    start: 0,
                    limit: 15
                },
                listeners: {
                    load: function(store)
                    { toolkit.web.intranet.applyClickToShowDetails('.intranet-today-mpe li', store); }
                }
            });
        }
        return this._store;
    },

    getPaging: function()
    {
        if(!this._paging)
        {
            this._paging = new Ext.PagingToolbar({
                store: this.getStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            })
        }
        return this._paging;
     },
});

