Ext._define('web.cms.post.RelateMetadata', {
    extend: 'Ext.Window',
    width: 545,
    modal: true,
    resizable: false,

    getStore: function()
    {
        if(!this._store)
        {
            this._store = Ext._create('Ext.data.JsonStore', {
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'value', 'unicode', 'fullname', 'key'],
                url: action('CMS/related_metadatas/json'),
                baseParams: { start: 0, limit: 50, content: this.content },
                scope: this,
                listeners: {
                    load:function()
                    {
                        Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                    },
                    scope:this
                }
            });
        }
        return this._store
    },

    getSiteMetadataWindow: function()
    {
        if(!this._siteMetadataWindow)
            this._siteMetadataWindow = Ext._create('Ext.Window', {
                width: 545,
                modal: true,
                resizable: false,
                items: [this.getSiteMetadataGrid(this.site)],
                buttons: [
                    {

                        scope: this,
                        tooltip: 'Adicionar marcadore(s)',
                        icon: icons+'add.png',
                        text: 'Adicionar marcadore(s)',
                        handler: function()
                        {
                            var metadatas = [],
                                grid = this.getSiteMetadataGrid(),
                                records = grid.getSelectionModel().getSelections();

                            if(records.length > 0)
                            {
                                Ext.each(records, function(item){
                                    metadatas.push(item.get('id'));
                                });

                                this.relateMetadata(metadatas, [this.content], grid);
                            }
                            else
                                Ext.Msg.alert('Aviso', 'Selecione ao menos um marcador');
                        }
                    }
                ],
                listeners: {
                    scope: this,
                    close: function()
                    {
                        this._siteMetadataWindow = null
                        this._siteMetadataGrid = null;
                        this.getGrid().getStore().reload();
                    }
                }
            });

        return this._siteMetadataWindow;
    },

    getSiteMetadataGrid: function()
    {
        if(!this._siteMetadataGrid)
            this._siteMetadataGrid = Ext._create('Ext.grid.GridPanel', {
                height: 400,
                border: false,
                store: Ext._create('Ext.data.JsonStore', {
                    autoLoad: true,
                    root: 'result',
                    totalProperty: 'total',
                    remoteSort: true,
                    fields: ['id', 'value', 'unicode', 'fullname', 'key'],
                    url: action('CMS/get_metadatas/json'),
                    baseParams: { start: 0, limit: 50, content: this.content, site: this.site },
                    scope: this
                }),
                columns: [
                    {dataIndex: 'key', header: 'Metadado', width: 250},
                    {dataIndex: 'value', header: 'Valor', width: 250}
                ]
            });

        return this._siteMetadataGrid;
    },

    getGrid: function()
    {
        if(!this._grid)
        {
            this._grid = Ext._create('Ext.grid.GridPanel', {
                height: 400,
                border: false,
                store: this.getStore(),
                tbar: [
                    {
                        scope: this,
                        tooltip: 'Selecionar marcadore(s)',
                        icon: icons+'status.png',
                        text: 'Selecionar marcadore(s)',
                        handler: function()
                        {
                            this.getSiteMetadataWindow().show();
                        }
                    }
                ],
                columns: [
                    {dataIndex: 'key', header: 'Metadado', width: 250},
                    {dataIndex: 'value', header: 'Valor', width: 250},
                    {
                        xtype: 'actioncolumn',
                        width: 30,
                        scope: this,
                        items: [
                            {
                                tooltip: 'Excluir',
                                getClass: function()
                                { return 'athenas-delete'; },
                                handler: function(grid, row, col)
                                {
                                    var rec = grid.getStore().getAt(row),
                                        _this = this;

                                    xConfirm({
                                        title: 'Confirmação',
                                        msg: 'Confirma a remoção da marca "'+ rec.get('fullname') +'" ?',
                                        fn: function(btn)
                                        {
                                            _this.relateMetadata([rec.get('id')], [_this.content], grid, true);
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

        return this._grid;
    },

    relateMetadata: function(metadatas, posts, grid, remove)
    {
        var target = toolkit.util.action('CMS/relate_metadata/json');
        if(remove)
            target = toolkit.util.action('CMS/unrelate_metadata/json')

        Ext.Ajax.request({
            url: target,
            method: 'POST',
            params: {
                contents: posts,
                metadatas: metadatas
            },
            success: function(response)
            {
                var obj = Ext.decode(response.responseText);
                if(obj.success)
                {
                    Ext.Msg.alert('Aviso', obj.msg);
                    grid.getStore().reload();
                }
            }
        });
    },

    constructor: function(cfg)
    {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Marcadores'
        });

        web.cms.post.RelateMetadata.superclass.constructor.call(this, cfg);

        this.add(this.getGrid());
    }
});

if(!toolkit.web.cms.Posts)
{
    toolkit.web.cms.Posts = Ext.extend(toolkit.widget.TabPanel, {
        constructor: function(site, kind, area, area_title, permissions, title)
        {
            this.site = site;
            this.kind = kind;
            this.area = area;
            this.area_title = area_title;
            this.perms = permissions;
            var options = {
                title: title,
                layout: 'fit',
                closable: true,
                defaults: {margins: '2 2 2 2'}
            };

            toolkit.web.cms.Posts.superclass.constructor.call(this, options);

            //toolkit.Application.tabspace.add(this);

            this.store = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'content', 'title', 'text', 'credits', 'tags', 'create_date',
                'position', 'published', 'published_date', 'publication_start', 'publication_end',
                'marked_as_published', 'can_share', 'as_link', 'is_index', 'link', 'no_searchable'],
                url: action('CMS/get_posts/json'),
                baseParams: { start: 0, limit: 20, area: this.area },
                scope: this,
                listeners: {
                    load:function()
                    {
                        Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                        Ext.select('.athenas-share').set({src: icons+'share.png'});
                        Ext.select('.athenas-published').set({src: icons+'published.png'});
                        Ext.select('.athenas-non-published').set({src: icons+'no-published.png'});
                    },
                    scope:this
                }
            });
            new Ext.LoadMask(Ext.getBody(), {msg: 'Por favor aguarde...', store: this.store});
            this.add(this.getPosts());
            this.doLayout();
        },

        getPosts: function()
        {
            if(!this.posts)
            {
                this.posts = new xGrid({
                    scope:this,
                    store:this.store,
                    selModel: Ext._create('Ext.grid.RowSelectionModel', {
                        singleSelect: true
                    }),
                    tbar:
                    [
                        {
                            tooltip: 'Novo Post',
                            icon: icons+'add.png',
                            text: 'Novo',
                            handler: function()
                            { this.makePostForm({title:'Adicionar Post', vals:{area:this.area, position:9999}}).show(); },
                            scope: this
                        },
                        '-',
                        {
                            tooltip: 'Marcadores',
                            icon: icons+'status.png',
                            text: 'Marcadores',
                            handler: function()
                            {

                                var records = this.posts.getSelectionModel().getSelections();
                                if(records.length > 0)
                                    Ext._create('web.cms.post.RelateMetadata', {
                                        site: this.site,
                                        content: records[0].get('id')
                                    }).show();
                                else
                                    Ext.Msg.alert('Aviso', 'Selecione um item.')
                            },
                            scope: this
                        },
                        {
                            tooltip: 'Áreas',
                            icon: icons+'show-areas.png',
                            text: 'Áreas',
                            handler: function()
                            { getAreaManager(this.site, this.kind, this.perms, this.area_title, true); },
                            scope: this
                        }
                    ],
                    columns:
                    [
                        {
                            id:'title', dataIndex:'title', header:'Título', width:450,
                            renderer:function(val){ return toolkit.util.replaceAll(val, '\\', ''); }
                        },
                        {
                            id:'credits', dataIndex:'credits', header:'Créditos', width:450,
                            renderer:function(val){ return toolkit.util.replaceAll(val, '\\', ''); }
                        },
                        {id:'published_date', dataIndex:'published_date', header:'Publicado em', width:100},
                        {
                            xtype: 'actioncolumn',
                            width: 115,
                            scope:this,
                            items: [
                                {
                                    tooltip:'Compartilhar',
                                    getClass:function(v, meta, rec, a, b)
                                    { return rec.get('can_share') ? 'athenas-share' : ''; },
                                    handler:function(grid, row, col)
                                    {
                                        var record = grid.getStore().getAt(row)
                                        var loading = new Ext.LoadMask(grid.getEl(), {msg: 'Por favor aguarde...'});
                                        loading.show();
                                        Ext.Ajax.request({
                                            url: toolkit.util.action('CMS/share/json'),
                                            params: {post: record.get('id')},
                                            success: function(request)
                                            {
                                                var json = Ext.decode(request.responseText);
                                                loading.hide();
                                                loading.destroy();
                                                Ext.Msg.alert('Aviso', json.msg);
                                            }
                                        })
                                    },
                                    scope:this
                                },
                                {
                                    tooltip:'Publicação',
                                    getClass:function(v, meta, rec, a, b)
                                    { return rec.get('marked_as_published') ? 'athenas-published' : 'athenas-non-published'; },
                                    handler:function(grid, row, col)
                                    {
                                        var pubForm = makePublicationForm({
                                            title: 'Publicação de Post',
                                            store: this.store,
                                            record: grid.getStore().getAt(row)
                                        });
                                    },
                                    scope:this
                                },
                                {
                                    tooltip:'Anexos',
                                    icon: icons+'attach.png',
                                    handler:function(grid, row, col)
                                    {
                                        var r = grid.getStore().getAt(row);
                                        getAttachmentsManager(r.get('id'), r.get('title'), true);
                                    },
                                    scope:this

                                },
                                {
                                    tooltip: 'Obter endereço do post',
                                    icon: icons + 'get_link.png',
                                    scope:this,
                                    handler: function(grid, row, col)
                                    {
                                        var keyMap = null;
                                        var record = grid.getStore().getAt(row);
                                        new xWindow({
                                            id:'URL-window',
                                            title: 'Endereço de Post',
                                            modal:true,
                                            items:
                                            [
                                                {
                                                    id:'url-to-copy',
                                                    xtype:'textfield',
                                                    fieldLabel: 'URL',
                                                    selectOnFocus:true,
                                                    value: record.get('link'),
                                                    readOnly: true,
                                                    width:400
                                                },
                                                {
                                                    id:'url-hint',
                                                    xtype:'displayfield',
                                                    html:'<span>Tecle CTRL+C para copiar</span>'
                                                },
                                                {
                                                    id:'select-url',
                                                    xtype:'button',
                                                    text:'Selecionar',
                                                    handler: function(btn)
                                                    {
                                                        btn.ownerCt.findById('url-to-copy').focus();
                                                        btn.setValue('Selecionar');
                                                    }
                                                }
                                            ],
                                            listeners:{
                                                show:function(component)
                                                {
                                                    keyMap = new Ext.KeyMap( component.el,
                                                        {
                                                            key: 'c',
                                                            ctrl:true,
                                                            fn: function()
                                                            {
                                                                var btnSelect = component.findById('select-url');
                                                                btnSelect.setText('Copiado!');
                                                                setTimeout(function(){ btnSelect.setText('Selecionar'); }, 1000);
                                                            }
                                                        }
                                                    );
                                                    component.findById('url-to-copy').focus(true, 100);
                                                },
                                                destroy: function()
                                                { keyMap.disable(); }
                                            }
                                        }).show();
                                    }

                                },
                                {
                                    tooltip:'Editar',
                                    icon: icons+'edit.png',
                                    handler: function(grid, row, col)
                                    {
                                        var r = grid.getStore().getAt(row);
                                        this.makePostForm({
                                            title:'Editar Post',
                                            vals:{
                                                area: this.area,
                                                id: r.get('id'),
                                                title: r.get('title'),
                                                text: r.get('text'),
                                                as_link: r.get('as_link'),
                                                is_index: r.get('is_index'),
                                                position:r.get('position'),
                                                tags: r.get('tags'),
                                                no_searchable: r.get('no_searchable')
                                            }
                                        }).show();
                                    },
                                    scope:this
                                },
                                {
                                    tooltip: 'Excluir',
                                    getClass: function(v, meta, rec, a, b)
                                    { return 'athenas-delete'; },
                                    handler: function(grid, row, col)
                                    {
                                        var rec = grid.getStore().getAt(row);

                                        xConfirm({
                                            title:'Confirmação',
                                            msg:'Confirma a exclusão do post: '+ rec.get('title') +' ?',
                                            fn: function(btn)
                                            {
                                                deleteItem({
                                                    signal: btn,
                                                    model: 'Post',
                                                    pars: rec.get('id'),
                                                    store: grid.getStore()
                                                });
                                            }
                                        });

                                    },
                                    scope: this
                                }
                            ]
                        }
                    ],
                    bbar: new Ext.PagingToolbar({
                        store: this.store,
                        displayInfo: true,
                        pageSize: 20,
                        prependButtons: true
                    })
                });
            }
            return this.posts;
        },

        makePostForm: function(opts)
        {
            return new ExtFormHelper({
                url: action('CMS/add_or_edit_post/json'),
                store: this.store,
                windowConfig: {
                    title: opts.title
                },
                formConfig: {
                    height: 550,
                    width: 660,
                    autoScroll: true,
                    items:[
                        {
                            name:'area',
                            value: opts.vals.area || '',
                            xtype:'hidden'
                        },
                        {
                            name:'id',
                            value: opts.vals.id || '',
                            xtype:'hidden'
                        },
                        {
                            name:'title',
                            fieldLabel:'Título',
                            value: toolkit.util.replaceAll(opts.vals.title, '\\', '') || '',
                            xtype:'textfield',
                            width:560
                        },
                        new toolkit.plugins.CKEditor({
                            name:'text',
                            fieldLabel:'Texto',
                            value: toolkit.util.replaceAll(opts.vals.text, '\\', '') || '',
                            toolbar: [
                                ['Source'], ['PasteFromWord'],
                                ['Link','Unlink'],
                                ['NumberedList','BulletedList'],
                                ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                            ],
                            autoScroll:true,
                            width:630,
                            height:320
                        }),
                        {
                            name:'as_link',
                            fieldLabel:'Disponível para link?',
                            value: opts.vals.as_link || '',
                            checked: opts.vals.as_link,
                            xtype:'checkbox',
                            width:170
                        },
                        {
                            name:'is_index',
                            fieldLabel:'Página principal?',
                            value: opts.vals.is_index || '',
                            checked: opts.vals.is_index,
                            xtype:'checkbox',
                            width:170
                        },
                        {
                            name:'no_searchable',
                            fieldLabel:'Remover da pesquisa?',
                            value: opts.vals.no_searchable || '',
                            checked: opts.vals.no_searchable,
                            xtype:'checkbox',
                            width:170
                        },
                        {
                            name:'position',
                            fieldLabel:'Posição',
                            value: opts.vals.position || '',
                            xtype:'textfield',
                            width:50
                        },
                        {
                            name:'tags',
                            fieldLabel:'Palavras-chave (Separadas por vírgula)',
                            value: opts.vals.tags || '',
                            xtype:'textfield',
                            width:620,
                            tabTip:'Separadas por vírgula'
                        }
                    ]
                }
            });
        }

    });
}
