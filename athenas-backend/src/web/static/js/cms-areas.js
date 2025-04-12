if(!toolkit.web.cms.Areas)
{
    toolkit.web.cms.Areas = Ext.extend(
        Ext.Window,
        {
            constructor: function(site, kind, permissions, area_title)
            {
                this.site = site;
                this.kind = kind;
                this.permissions = permissions;
                this.area_title = area_title;
                var options = {
                    title: 'Áreas de '+area_title,
                    modal:true,
                    layout:'fit',
                    height: 350,
                    width: 500,
                    defaults:{margins:'2 2 2 2'}
                };

                toolkit.web.cms.Areas.superclass.constructor.call(this, options);

                this.store = new xJsonStore({
                    autoLoad:true,
                    root: 'result',
                    totalProperty: 'total',
                    remoteSort: true,
                    fields: ['id', 'name', 'kind_of_content', 'fullname', 'parent', 'as_link', 'can_share', 'items_no_searchable'],
                    proxy: new Ext.data.HttpProxy({
                        method:'GET',
                        url: action('CMS/get_areas/json')
                    }),
                    baseParams: { start: 0, end: 50, site: this.site, kind: this.kind },
                    scope: this,
                    listeners: {
                        load: function()
                        {
                            //Ext.select('.athenas-subarea').set({src: icons+'add.png'});
                            Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                            Ext.select('.athenas-edit').set({src: icons+'edit.png'});
                            Ext.select('.athenas-users').set({src: icons+'users.png'});
                            //Ext.select('.athenas-links').set({src: icons+'link.png'});
                            //Ext.select('.athenas-posts').set({src: icons+'show-areas.png'});
                            Ext.select('.athenas-show-areas').set({src: icons+'show-areas.png'});
                        },
                        scope:this
                    }
                });
                new Ext.LoadMask(Ext.getBody(), {msg: 'Por favor aguarde...', store: this.store});
                this.add(this.getAreas());
                this.doLayout();
            },
            getAreas: function()
            {
                var _tbar = [];
                if(this.permissions.is_superuser)
                {
                    _tbar = [
                        {
                            tooltip: 'Adicionar',
                            icon: icons+'add.png',
                            text: 'Novo',
                            handler: function()
                            {
                                this.makeForm({
                                    title: 'Adicionar Área',
                                    vals: {
                                        parent: this.site,
                                        kind_of_content: this.kind
                                    }
                                }).show();
                            },
                            scope: this
                        },
                        {
                            tooltip: 'Excluir Selecionados',
                            icon: icons+'delete.png',
                            text: 'Excluir Selecionados',
                            handler: function()
                            {
                                pars = []
                                Ext.each(
                                    this.getAreas().getSelectionModel().getSelections(),
                                    function(item, index){ pars[index] = item.get('id'); }
                                )
                                pars = pars.join(',');
                                xConfirm({
                                    title:'Confirmação',
                                    msg:'Confirma a exclusão dos itens selecionados?',
                                    fn:function(btn)
                                    {
                                        deleteItem({
                                            signal:btn,
                                            model:'Area',
                                            pars:pars,
                                            store:this.store
                                        });
                                    },
                                    scope:this
                                });
                            },
                            scope:this
                        },
                        '-'
                    ];
               }

               _tbar[_tbar.length] = {
                    tooltip:'Sites',
                    icon: icons+'applications-internet.png',
                    text: 'Sites',
                    handler: function()
                    {
                        getSiteManager(true, this.permissions);
                        toolkit.web.cms.areaManager.hide();
                    },
                    scope:this
                };

               if(!this.areas)
               {
                    Ext.QuickTips.init();

                    var kind = this.kind.toLowerCase();
                    var manager = {
                        tooltip: 'Visualizar posts',
                        icon: icons+'show-areas.png',
                        handler: function(grid, row, col)
                        {
                            var record = grid.getStore().getAt(row);
                            getPostManager(this.site, kind, record.get('id'), this.area_title, this.permissions, record.get('fullname'), true);
                            toolkit.web.cms.areaManager.hide();
                        }
                    }

                    if (kind == 'link')
                    {
                        manager = {
                            tooltip: 'Visualizar links',
                            icon: icons+'show-areas.png',
                            handler: function(grid, row, col)
                            {
                                var record = grid.getStore().getAt(row)
                                getLinkManager(this.site, kind, record.get('id'), this.area_title, this.permissions, record.get('fullname'), true);
                                toolkit.web.cms.areaManager.hide();
                            }
                        }
                    }
                    else if (kind == 'pgj-actions')
                    {
                        manager = {
                            tooltip: 'Visualizar atuações',
                            icon: icons+'show-areas.png',
                            handler: function(grid, row, col)
                            {
                                var record = grid.getStore().getAt(row)
                                getPGJActionsManager(this.site, kind, record.get('id'), this.area_title, this.permissions, record.get('fullname'), true);
                                toolkit.web.cms.areaManager.hide();
                            }
                        }
                    }

                    this.areas = new Ext.grid.GridPanel({
                        scope: this,
                        region: 'center',
                        border: true,
                        store: this.store,
                        tbar: _tbar,
                        columns:
                        [
                            {id: 'name', dataIndex: 'fullname', header: 'Nome', sortable: true, width: 368},
                            {
                                xtype: 'actioncolumn',
                                header: 'Controles',
                                width: 100,
                                scope: this,
                                items: [
                                    {
                                        tooltip: 'Excluir',
                                        getClass: function(v, meta, rec, a, b)
                                        { return (this.permissions.is_superuser) ? 'athenas-delete' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var rec = grid.getStore().getAt(row);

                                            xConfirm({
                                                title: 'Confirmação',
                                                msg: 'Confirma a exclusão da área: '+ rec.get('name') +' ?',
                                                fn: function(btn)
                                                {
                                                    deleteItem({
                                                        signal: btn,
                                                        model: 'Area',
                                                        pars: rec.get('id'),
                                                        store: grid.getStore()
                                                    });

                                                }
                                            });

                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Editar',
                                        getClass: function(v, meta, rec, a, b)
                                        { return (this.permissions.is_superuser) ? 'athenas-edit' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var r = grid.getStore().getAt(row)
                                            this.makeForm({
                                                title:'Editar Área',
                                                vals: {
                                                    id: r.get('id'),
                                                    name: r.get('name'),
                                                    kind_of_content: r.get('kind_of_content'),
                                                    parent: r.get('parent'),
                                                    as_link: r.get('as_link'),
                                                    can_share: r.get('can_share'),
                                                    items_no_searchable: r.get('items_no_searchable')
                                                }
                                            }).show();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Adicionar sub área',
                                        getClass: function(v, meta, rec, a, b)
                                        { return (rec.get('parent')==null && this.permissions.is_superuser) ? 'athenas-subarea' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var r = grid.getStore().getAt(row);
                                            this.makeForm({
                                                title:'Adicionar Sub Área',
                                                vals:{parent:r.get('id'), store:grid.getStore()}
                                            }).show();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Usuários da área',
                                        getClass:function(v, meta, rec, a, b)
                                        { return (rec.get('parent') != null && this.permissions.is_superuser) ? 'athenas-users' : ''; },
                                        handler:function(grid, row, col)
                                        {
                                            var r = grid.getStore().getAt(row)
                                            getPermissionsManager(r.get('id'), this.permissions, true);
                                            //toolkit.web.cms.areaManager.hide();
                                        },
                                        scope:this
                                    },
                                    manager
                                ]
                            }
                        ]
                   });
               }
               return this.areas;
            },

            makeForm: function(opts)
            {
                return formMaker({
                    title: opts.title,
                    url: action('CMS/add_or_edit_area/json'),
                    width: 230,
                    height: 220,
                    store: this.store,
                    items: [
                        {
                            name:'id',
                            value: opts.vals.id || '',
                            xtype:'hidden'
                        },
                        {
                            name:'parent',
                            value: this.site,
                            xtype:'hidden'
                        },
                        {
                            name: 'kind_of_content',
                            xtype: 'hidden',
                            value: this.kind,
                        },
                        {
                            fieldLabel:'Nome',
                            name:'name',
                            value: opts.vals.name || '',
                            width:170,
                            xtype:'textfield'
                        },
                        {
                            fieldLabel:'Disponível para link?',
                            name:'as_link',
                            value: opts.vals.as_link || '',
                            checked: opts.vals.as_link,
                            width:170,
                            xtype:'checkbox'
                        },
                        {
                            fieldLabel:'Compartilhar em redes sociais?',
                            name:'can_share',
                            value: opts.vals.can_share || '',
                            checked: opts.vals.can_share,
                            width:170,
                            xtype:'checkbox'
                        },
                        {
                            fieldLabel:'Remover itens da pesquisa?',
                            name:'items_no_searchable',
                            value: opts.vals.items_no_searchable || '',
                            checked: opts.vals.items_no_searchable,
                            width:170,
                            xtype:'checkbox'
                        }
                    ]
                });
            }
        }
    );
}

