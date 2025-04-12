Ext.ns('toolkit.web.cms.links');

toolkit.web.cms.links.onNodeClick = function(node)
{
    var manager = Ext.getCmp('cms-links-manager');
    var store = manager.getGrid().getStore();

    new Ext.LoadMask(manager.getGrid().getEl(), {msg: 'Aguarde...', store: store});

    if(node.attributes.isSuperior)
        manager.getGrid().getTopToolbar().enable();
    else
        manager.getGrid().getTopToolbar().disable();

    store.bag.parent = node.id;
    store.bag.parentTitle = node.text;
    store.load({params: {parent: node.id, parentTitle: node.text}});
}

toolkit.web.cms.links.onNodeExpand = function(node)
{
    node.eachChild(function(){
        this.setText(toolkit.util.replaceAll(this.text, '\\', ''))
        this.on('click', toolkit.web.cms.links.onNodeClick);
        this.on('expand', toolkit.web.cms.links.onNodeExpand);
    });
    node.fireEvent('click', node);
}

toolkit.web.cms.links.Manager = Ext.extend(toolkit.widget.TabPanel, {

    constructor: function(site, kind, area, area_title, permissions, title)
    {
        this.site = site;
        this.kind = kind;
        this.area = area;
        this.title = title;
        this.area_title = area_title;
        this.perms = permissions;

        toolkit.web.cms.links.Manager.superclass.constructor.call(this, {
            id: 'cms-links-manager',
            title: title,
            closable: true,
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            tbar: [
                {
                    tooltip:'Áreas',
                    icon: icons+'show-areas.png',
                    text: 'Áreas',
                    handler: function()
                    { getAreaManager(this.site, this.kind, this.perms, this.area_title, true); },
                    scope: this
                }
            ],
            items: [
                this.getTree(),
                this.getGrid()
            ]
        });

        // var cmp = toolkit.Application.tabspace.findById('cms-links-manager');
        // if (cmp)
        //     cmp.destroy();

        //toolkit.Application.tabspace.add(this);
    },

    getTree: function()
    {
        if(!this._treeLinks)
        {
            this._treeLinks = new Ext.tree.TreePanel({
                title: 'Visualização',
                autoScroll: true,
                animate: true,
                containerScroll: true,
                width: 300,
                bodyStyle: {
                    padding: '5px'
                },
                loader: new Ext.tree.TreeLoader({
                    dataUrl: action('CMS/get_links_by_level/json'),
                    baseParams: {area: this.area},
                    nodeParameter: 'parent'
                }),
                root: {
                    nodeType: 'async',
                    text: this.title,
                    isSuperior: true,
                    expanded: true,
                    id: 'root',
                    listeners: {
                        click: toolkit.web.cms.links.onNodeClick,
                        expand: toolkit.web.cms.links.onNodeExpand
                    }
                }
            });
        }
        return this._treeLinks;
    },

    getGrid: function()
    {
        if(!this._gridLinks)
        {
            this._gridLinks = new Ext.grid.GridPanel({
                title: 'Edição',
                scope: this,
                flex: 1,
                store: this.getGridStore(),
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                tbar: [
                    {
                        tooltip: 'Novo Link',
                        icon: icons+'add.png',
                        text: 'Novo',
                        handler: function()
                        {
                            var store = this.getGridStore();
                            this.makeForm({
                                title: 'Adicionar Link',
                                vals: {
                                    area: this.area,
                                    parent: store.bag.parent || 'root',
                                    parentTitle: store.bag.parentTitle || '',
                                    image_url: '/'+ CONTEXT +'/static/web/icons/no-image.jpg',
                                    position: 9999
                                }
                            }).show();
                        },
                        scope: this
                    }
                ],
                columns:[
                    {
                        id: 'title', dataIndex: 'fullname', header: 'Título', width: 450,
                        renderer: function(val){ return toolkit.util.replaceAll(val, '\\', ''); }
                    },
                    {
                        id:'credits', dataIndex:'credits', header:'Créditos', width:450,
                        renderer: function(val){ return toolkit.util.replaceAll(val, '\\', ''); }
                    },
                    {
                        xtype: 'actioncolumn',
                        width: 60,
                        scope: this,
                        items: [
                            {
                                tooltip: 'Publicação',
                                getClass: function(value, meta, record, a, b)
                                { return record.get('marked_as_published') ? 'athenas-published' : 'athenas-non-published'; },
                                handler: function(grid, row, col)
                                {
                                    var pubForm = makePublicationForm({
                                        title: 'Publicação de Link',
                                        store: grid.getStore(),
                                        record: grid.getStore().getAt(row),
                                        cascade: true
                                    });
                                },
                                scope: this
                            },
                            {
                                tooltip: 'Visualizar ou Editar',
                                icon: icons+'edit.png',
                                handler: function(grid, row)
                                {
                                    var record = grid.getStore().getAt(row);
                                    this.makeForm({
                                        title: 'Editar Link',
                                        vals: {
                                            area: this.area,
                                            parent: record.get('parent'),
                                            id: record.get('id'),
                                            parentTitle: record.get('parent_title'),
                                            title: record.get('title'),
                                            url: record.get('url'),
                                            position: record.get('position'),
                                            kind: record.get('kind'),
                                            image_url: record.get('image_url')
                                        }
                                    }).show();
                                },
                                scope: this
                            },
                            {
                                tooltip: 'Excluir',
                                icon: icons+'delete.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row),
                                        tree = this.getTree();

                                    xConfirm({
                                        title: 'Confirmação',
                                        msg: 'Confirma a exclusão do link: '+ record.get('title') +' ?',
                                        fn: function(btn)
                                        {
                                            deleteItem({
                                                signal: btn,
                                                model: 'Link',
                                                pars: record.get('id'),
                                                //store: grid.getStore(),
                                                success: function()
                                                {
                                                    var id = grid.getStore().bag.parent || 'root',
                                                        node = tree.getNodeById(id);
                                                    node.reload();
                                                }
                                            });
                                        }
                                    });
                                },
                                scope: this
                            }
                        ]
                    }
                ]
            });
        }
        return this._gridLinks;
    },

    getGridStore: function()
    {
        if(!this._gridStore)
        {
            this._gridStore = new Ext.data.JsonStore({
                bag: {},
                scope: this ,
                root: 'result',
                totalProperty: 'total',
                url: action('CMS/get_links/json'),
                baseParams: {start: 0, end: 10, area: this.area, parent: 'root', parentTitle: ''},
                fields: ['id', 'content', 'title', 'credits', 'create_date', 'url', 'published',
                    'image_url', 'position', 'parent', 'parent_title', 'published_date',
                    'publication_start', 'publication_end', 'marked_as_published', 'fullname', 'kind'],
                listeners: {
                    load: function(store, record, options)
                    {
                        Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                        Ext.select('.athenas-published').set({src: icons+'published.png'});
                        Ext.select('.athenas-non-published').set({src: icons+'no-published.png'});
                    },
                    scope: this
                }
            });
        }
        return this._gridStore;
    },

    makeForm: function(opts)
    {
        var store = new Ext.data.JsonStore({
            autoLoad: true,
            root: 'result',
            totalProperty: 'total',
            fields: ['id', 'title', 'fullname', 'slug', 'kind'],
            baseParams:{ area: this.area, exclude: opts.vals.id },
            url: action('CMS/get_superior_links/json')
        });

        var store_available = new Ext.data.JsonStore({
            //autoLoad: true,
            root: 'result',
            totalProperty: 'total',
            fields: ['id', 'name', 'fullname', 'slug', 'kind', 'url'],
            baseParams: {area: this.site, posts: 1},
            url: action('CMS/get_links_for_menu/json')
        });

        var store_site_url = new Ext.data.JsonStore({
            //autoLoad: true,
            root: 'result',
            totalProperty: 'total',
            fields: ['url'],
            baseParams: {site: this.site},
            url: action('CMS/get_site_url/json')
        });

        var kinds =  [
            {xtype: 'radio', boxLabel: 'Externo', name: 'kind', inputValue: 1},
            {xtype: 'radio', boxLabel: 'Superior', name: 'kind', inputValue: 0},
            {xtype: 'radio', boxLabel: 'Área', name: 'kind', inputValue: 2},
            {xtype: 'radio', boxLabel: 'Página', name: 'kind', inputValue: 3},
            {xtype: 'radio', boxLabel: 'Galeria', name: 'kind', inputValue: 4}
        ];

        var checkedRadio = null;
        Ext.each(kinds, function(item) {
            if(item.inputValue == opts.vals.kind)
            {
                item.checked = true;
                checkedRadio = item;
            }
        });

        var tree = this.getTree()
        var form = new ExtFormHelper({
            url: action('CMS/add_or_edit_link/json'),
            //store: this.getGridStore(),
            success: function(cmp, action)
            {
                var id = opts.vals.parent || 'root',
                    node = tree.getNodeById(id);
                node.reload();
            },
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                height: 500,
                width: 450,
                autoScroll: true,
                fileUpload: true,
                items: [
                    {
                        name: 'area',
                        value: opts.vals.area || '',
                        xtype: 'hidden'
                    },
                    {
                        name: 'id',
                        value: opts.vals.id || '',
                        xtype: 'hidden'
                    },
                    {
                        xtype: 'radiogroup',
                        fieldLabel: 'Tipo de Link',
                        itemCls: 'x-check-group-alt',
                        name: 'kinds',
                        items: kinds,
                        listeners: {
                            change: function(group, checked)
                            {
                                if(checked)
                                {
                                    var trueForm = form.items.items[0],
                                        value = checked.inputValue,
                                        available = getFieldByName(trueForm, 'available-items'),
                                        checkSame = getFieldByName(trueForm, 'same-title'),
                                        urlField = getFieldByName(trueForm, 'url');

                                    if(value == 0 || value == 1)
                                    {
                                        urlField.setReadOnly(false);
                                        available.hide();
                                        checkSame.hide();

                                        if(value == 0)
                                            urlField.setValue('#');
                                        // else if(value == 1)
                                        //     urlField.setValue('');
                                    }
                                    else
                                    {
                                        if(value == 4)
                                        {
                                            getFieldByName(trueForm, 'title').setValue('Galerias');
                                            store_site_url.on('load', function(){
                                                var site_url = store_site_url.getAt(0).get('url')
                                                urlField.setValue(site_url+'/galerias');
                                                urlField.setReadOnly(true);
                                                available.hide();
                                                checkSame.hide();
                                            });
                                            store_site_url.load();
                                        }
                                        else
                                        {
                                            new Ext.LoadMask(form.getEl(), {msg: 'Aguarde...', store: store_available});

                                            var loadOpts = {};
                                            if (value == 2)
                                                loadOpts = {params: {posts: 0}};

                                            store_available.on('load',
                                                function(store)
                                                {
                                                    var availableId = null;
                                                    store.each(function(record){
                                                        if(opts.vals.url && opts.vals.url.indexOf( record.get('slug') ) > -1)
                                                            available.setValue(record.get('id'));
                                                    });
                                                    available.show();
                                                    checkSame.show();
                                                }
                                            );
                                            store_available.load(loadOpts);
                                        }
                                    }
                                }
                            }
                        }
                    },
                    {
                        name: 'available-items',
                        fieldLabel: 'Itens disponíveis',
                        xtype: 'combo',
                        triggerAction: 'all',
                        hidden: true,
                        typeAhead: true,
                        mode: 'local',
                        width: 420,
                        store: store_available,
                        valueField: 'id',
                        displayField: 'fullname',
                        resizable: true,
                        listeners: {
                            select: function(cmp, record, index)
                            {
                                var urlField = getFieldByName(form.items.items[0], 'url');
                                urlField.setReadOnly(false);
                                urlField.setValue(record.get('url'));
                                urlField.setReadOnly(true);
                            }
                        }
                    },
                    {
                        xtype: 'checkbox',
                        fieldLabel: 'Mesmo título do item disponível?',
                        name: 'same-title',
                        hidden: true,
                        listeners: {
                            check: function(cmp, checked)
                            {
                                if(checked)
                                {
                                    var titleField = getFieldByName(form.items.items[0], 'title'),
                                        availableItemsField = getFieldByName(form.items.items[0], 'available-items'),
                                        store = availableItemsField.getStore();

                                    store.each(function(record){
                                        if(record.get('id') == availableItemsField.getValue())
                                        {
                                            titleField.setValue(record.get('name'));
                                            return false;
                                        }
                                    });
                                }
                            }
                        }
                    },
                    {
                        name: 'title',
                        fieldLabel: 'Título',
                        value: toolkit.util.replaceAll(opts.vals.title, '\\', '') || '',
                        xtype: 'textfield',
                        width: 420
                    },
                    {
                        name: 'position',
                        fieldLabel: 'Posição',
                        value: opts.vals.position || '',
                        xtype: 'textfield',
                        width: 50
                    },
                    {
                        name: 'url',
                        fieldLabel: 'URL',
                        value: opts.vals.url || '',
                        xtype: 'textfield',
                        width: 420
                    },
                    {
                        fieldLabel: 'Link Superior',
                        store: store,
                        xtype: 'combo',
                        triggerAction: 'all',
                        mode: 'local',
                        width: 420,
                        resizable: true,
                        hiddenName: 'parent',
                        hiddenValue: (opts.vals.parent=='root') ? '' : opts.vals.parent,
                        value: opts.vals.parentTitle || '',
                        valueField: 'id',
                        displayField: 'fullname'
                    },
                    {
                        name: 'image',
                        fieldLabel: 'Imagem',
                        xtype: 'fileuploadfield',
                        width: 420
                    },
                    {
                        fieldLabel: 'Imagem atual',
                        xtype: 'displayfield',
                        html: '<img src="'+opts.vals.image_url+'">'
                    }
                ]
            }
        });

        form.on('afterrender',
            function(c)
            {
                var radioGroup = getFieldByName(form.items.items[0], 'kinds');
                radioGroup.fireEvent('change', radioGroup, checkedRadio);
            }
        );

        return form;
    }
});


