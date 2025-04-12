if(!toolkit.web.cms.Sites)
{
    toolkit.web.cms.Sites = Ext.extend(
        Ext.Window,
        {
            constructor: function(permissions)
            {
                this.permissions = permissions;
                var options = {
                    title: 'Sites',
                    modal:true,
                    layout:'fit',
                    height: 350,
                    width: 540,
                    defaults:{margins: '2 2 2 2'}
                };

                toolkit.web.cms.Sites.superclass.constructor.call(this, options);

                this.modules_store = new Ext.data.JsonStore({
                    autoLoad: true,
                    root: 'result',
                    totalProperty: 'total',
                    remoteSort: true,
                    fields: ['id', 'name', 'slug'],
                    proxy: new Ext.data.HttpProxy({
                        method: 'GET',
                        url: action('CMS/get_modules/json')
                    })
                });

                this.store = new Ext.data.JsonStore({
                    autoLoad:true,
                    root: 'result',
                    totalProperty: 'total',
                    remoteSort: true,
                    fields: ['id', 'name', 'fullname', 'slug', 'parent', 'as_link', 'modules'],
                    proxy: new Ext.data.HttpProxy({
                        method:'GET',
                        url: action('CMS/get_sites/json')
                    }),
                    baseParams:{ start:0, end:50 },
                    scope: this,
                    listeners:{
                        load: function()
                        {
                            Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                            Ext.select('.athenas-edit').set({src: icons+'edit.png'});
                            Ext.select('.athenas-users').set({src: icons+'users.png'});
                            Ext.select('.athenas-posts').set({src: icons+'posts-view.png'});
                            Ext.select('.athenas-links').set({src: icons+'link.png'});
                            Ext.select('.athenas-polls').set({src: icons+'poll.png'});
                            Ext.select('.athenas-pgj-actions').set({src: icons+'pgj-actions.png'});
                            Ext.select('.athenas-metadata').set({src: icons+'status.png'});

                            if (this.download)
                            {
                                xAlert({msg:'<a href="'+this.download+'">Download do pacote do aplicativo</a>'});
                                this.download = null;
                            }
                        },
                        scope:this
                    }
                });
                new Ext.LoadMask(Ext.getBody(), {msg:'Por favor aguarde...', store:this.store});
                this.add(this.getSites());
                this.doLayout();
            },

            _hasModule: function(module, modules)
            {
                var has = false;
                Ext.each(modules, function(item){
                    if(item.slug == module)
                    {
                        has = true;
                        return false;
                    }
                });
                return has;
            },

            getSites: function()
            {
               if(!this.sites)
               {
                    Ext.QuickTips.init();

                    this.sites = new xGrid({
                        scope:this,
                        region:'center',
                        border:true,
                        store: this.store,
                        tbar: (this.permissions.is_superuser) ?
                        [
                            {
                                tooltip:'Adicionar',
                                icon: icons+'add.png',
                                text: 'Novo',
                                handler: function()
                                { this.makeForm({title:'Adicionar Site', vals:{}}).show(); },
                                scope: this
                            },
                            {
                                tooltip:'Excluir Selecionados',
                                icon: icons+'delete.png',
                                text: 'Excluir Selecionados',
                                handler: function()
                                {
                                    pars = []
                                    Ext.each(
                                        this.getSites().getSelectionModel().getSelections(),
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
                            }
                        ] : null,
                        columns:
                        [
                            {id:'name', dataIndex:'fullname', header:'Nome', sortable:true, width:340},
                            {
                                xtype: 'actioncolumn',
                                header:'Controles',
                                width: 160,
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
                                                title:'Confirmação',
                                                msg:'Confirma a exclusão do site: '+ rec.get('name') +' ?',
                                                fn: function(btn)
                                                {
                                                    deleteItem({
                                                        signal:btn,
                                                        model:'Area',
                                                        pars:rec.get('id'),
                                                        store:grid.getStore()
                                                    });

                                                }
                                            });

                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Editar',
                                        style: { margin: '0 3px 0 2px' },
                                        getClass: function()
                                        { return (this.permissions.is_superuser) ? 'athenas-edit' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var record = grid.getStore().getAt(row)
                                            this.makeForm({
                                                title: 'Editar Site',
                                                vals: {
                                                    id: record.get('id'),
                                                    name: record.get('name'),
                                                    //as_link: record.get('as_link'),
                                                    modules: record.get('modules')
                                                }
                                            }).show();

                                        },
                                        scope: this
                                    },
                                    {
                                        tooltip:'Usuários',
                                        getClass:function()
                                        { return (this.permissions.is_superuser) ? 'athenas-users' : ''; },
                                        handler:function(grid, row, col)
                                        {
                                            var r = grid.getStore().getAt(row)
                                            getPermissionsManager(r.get('id'), this.permissions, true);
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Acessar Posts',
                                        getClass: function(v, meta, record)
                                        { return (this._hasModule('posts', record.get('modules'))) ? 'athenas-posts' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var r = grid.getStore().getAt(row);
                                            getAreaManager(r.get('id'), 'post', this.permissions, r.get('fullname'), true);
                                            toolkit.web.cms.siteManager.hide();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Acessar Links',
                                        getClass: function(v, meta, record)
                                        { return (this._hasModule('links', record.get('modules'))) ? 'athenas-links' : '';},
                                        handler: function(grid, row, col)
                                        {
                                            var r = grid.getStore().getAt(row);
                                            getAreaManager(r.get('id'), 'link', this.permissions, r.get('fullname'), true);
                                            toolkit.web.cms.siteManager.hide();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Visualizar enquetes',
                                        getClass: function(v, meta, record)
                                        { return (this._hasModule('polls', record.get('modules'))) ? 'athenas-polls' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var record = grid.getStore().getAt(row);
                                            getPollManager(record.get('id'), this.permissions, record.get('fullname'), true);
                                            toolkit.web.cms.siteManager.hide();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Visualizar categorias',
                                        getClass: function(v, meta, record)
                                        { return 'tag-icon' },
                                        handler: function(grid, row, col)
                                        {
                                            var record = grid.getStore().getAt(row);
                                            Ext._create('web.cms.category.Manager', {
                                                state: {
                                                    site_pk: record.get('id'),
                                                    site: record.get('slug')
                                                }
                                            })
                                            
                                            toolkit.web.cms.siteManager.hide();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Visualizar Metadados',
                                        getClass: function(v, meta, record)
                                        { return 'athenas-metadata'; },
                                        handler: function(grid, row, col)
                                        {
                                            var record = grid.getStore().getAt(row);
                                            Ext._create('web.cms.metadata.MetaValueManager', {
                                                title: 'Gerenciador de Metadados de ' + record.get('name'),
                                                site: record.get('id')
                                            }).show();
                                            toolkit.web.cms.siteManager.hide();
                                        },
                                        scope:this
                                    },
                                    {
                                        tooltip:'Visualizar atuações do MPE',
                                        getClass: function(v, meta, record)
                                        { return (this._hasModule('pgj-actions', record.get('modules'))) ? 'athenas-pgj-actions' : ''; },
                                        handler: function(grid, row, col)
                                        {
                                            var record = grid.getStore().getAt(row);
                                            getAreaManager(record.get('id'), 'pgj-actions', this.permissions, record.get('fullname'), true);
                                            toolkit.web.cms.siteManager.hide();
                                        },
                                        scope:this
                                    }
                                ]
                            }
                        ]
                   });
               }
               return this.sites;
            },

            // getCategoriesGrid: function (cfg) {
            //     if (!this._categoriesGrid) {
            //         this._categoriesGrid = Ext._create('web.cms.category.Grid', {
            //             region: 'center',
            //             gridAutoLoad: false,
            //         });

            //         var filter = [
            //             {
            //                 property: 'sites__slug',
            //                 value: cfg.state.site,
            //                 stage: 1000,
            //             },
            //         ];

            //         if (this.category_id)
            //             filter.push({
            //                 property: 'parent',
            //                 value: this.category_id,
            //                 stage: 2000,
            //             });

            //         this._categoriesGrid.setFilter(filter);
            //     }

            //     return this._categoriesGrid;
            // },

            makeForm: function(opts)
            {
                var modules = [];
                this.modules_store.each(function(record){
                    var module = {boxLabel: record.get('name'), name: 'modules', inputValue: record.get('id')};
                    Ext.each(opts.vals.modules, function(item){
                        if(item.slug == record.get('slug'))
                            module.checked = true;
                    });
                    modules[modules.length] = module;
                });

                var $this = this;
                var auto_create = {};
                var height = 245;
                var fields = [
                    {
                        name: 'id',
                        value: opts.vals.id || '',
                        xtype: 'hidden'
                    },
                    {
                        name: 'kind_of_content',
                        value: 'area',
                        xtype: 'hidden'
                    },
                    {
                        fieldLabel: 'Nome',
                        name: 'name',
                        value: opts.vals.name || '',
                        width: 250,
                        xtype: 'textfield'
                    },
                    {
                        fieldLabel:'Módulos',
                        name: 'modules',
                        width: 250,
                        xtype: 'checkboxgroup',
                        style: {
                            padding: '0 10px',
                            marginBottom: '10px'
                        },
                        columns: 2,
                        items: modules
                    }
                ];

                if(!opts.vals.id)
                {
                    height = 285;
                    fields = fields.concat([
                        {
                            fieldLabel: 'Criar site base?',
                            name: 'auto_create',
                            xtype: 'checkbox'
                        },
                        {
                            fieldLabel: 'Título do Site',
                            name: 'title',
                            width: 250,
                            xtype: 'textfield'
                        }
                    ]);
                }

                return ExtFormHelper({
                    url: action('CMS/add_or_edit_area/json'),
                    store: this.store,
                    success: function(form, action)
                    {
                        var response = eval('('+ action.response.responseText +')');
                        $this.download = response.download;
                    },

                    windowConfig: {
                        title: opts.title,
                    },

                    formConfig: {
                        height: height,
                        autoWidth: true,
                        autoHeight: true,
                        items: fields,
                        defaults: {
                            style: {
                                marginBottom: '10px'
                            }
                        }
                    }
                });
            }
        }
    );
}
