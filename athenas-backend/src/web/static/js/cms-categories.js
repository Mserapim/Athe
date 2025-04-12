if(!toolkit.web.cms.Categories)
{
    toolkit.web.cms.Categories = xt.extend(xWindow, {
        constructor: function(id, title, by)
        {
            if(by == 'area') this.area = id;
            else this.content = id;

            var options = {
                title: title,
                region:'center',
                modal:true,
                layout:'fit',
                height: 350,
                width: 430,
                defaults:{margins:'2 2 2 2'}
            };

            toolkit.web.cms.Categories.superclass.constructor.call(this, options);

            this.store = new xJsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'name', 'area', 'create_date'],
                url: action('CMS/get_categories/json'),
                baseParams:{ start:0, end:50, area:this.area, content:this.content },
                scope:this,
                listeners:{
                    load:function()
                    {
                        toolkit.web.cms.postManager.getPosts().getTopToolbar().items.get('combo-categories').getStore().reload();
                        xt.select('.athenas-link').set({src:icons+'link.png'});
                        xt.select('.athenas-delete').set({src:icons+'delete.png'});
                    },
                    scope:this
                }
            });
            new xt.LoadMask(xt.getBody(), {msg:'Por favor aguarde...', store:this.store});
            var grid = (by=='area') ? this.getCategories() : this.getRelCategories();
            this.add(grid);
            this.doLayout();
        },

        getCategories: function()
        {
            if(!this.categories)
            {
                this.categories = new xGrid({
                    height:250,
                    scope:this,
                    store:this.store,
                    tbar:[
                        {
                            tooltip:'Nova Categoria',
                            icon: icons+'add.png',
                            text: 'Nova',
                            handler: function()
                            {
                                this.makeForm({title:'Adicionar Categoria', vals:{area:this.area}}).show();
                            },
                            scope:this
                        }
                    ],
                    columns:[
                        {dataIndex:'name', header:'Nome', width:340},
                        {
                            xtype:'actioncolumn',
                            width:60,
                            scope:this,
                            items:[
                                {
                                    tooltip:'Visualizar ou Editar',
                                    icon: icons+'edit.png',
                                    handler:function(grid, row)
                                    {
                                        var r = grid.getStore().getAt(row);
                                        this.makeForm({
                                            title:'Editar Categoria',
                                            vals:{id:r.get('id'), area:this.area, name:r.get('name')}
                                        }).show();
                                    },
                                    scope:this
                                },
                                {
                                    tooltip:'Excluir',
                                    icon: icons+'delete.png',
                                    handler:function(grid, row, col)
                                    {
                                        var rec = grid.getStore().getAt(row);

                                        xConfirm({
                                            title:'Confirmação',
                                            msg:'Confirma a exclusão da categoria: '+ rec.get('name') +' ?',
                                            fn: function(btn)
                                            {
                                                deleteItem({
                                                    signal: btn,
                                                    model: 'Category',
                                                    pars: rec.get('id'),
                                                    store: grid.getStore()
                                                });
                                            }
                                        });

                                    },
                                    scope:this
                                }
                            ]
                        }
                    ]
                });
            }
            return this.categories;
        },

        getRelCategories: function()
        {
           return new xGrid({
                height:250,
                scope:this,
                store:this.store,
                columns:[
                    {dataIndex:'name', header:'Nome', width:380},
                    {
                        xtype:'actioncolumn',
                        width:25,
                        scope:this,
                        items:[
                            {
                                tooltip:'Descategorizar',
                                icon: icons+'un-assoc-category.png',
                                handler:function(grid, row, col)
                                {
                                    var r = grid.getStore().getAt(row);
                                    xAjax.request({
                                        url:action('CMS/categorize_uncategorize/json'),
                                        params: {category:r.get('id'), contents:this.content, action:'remove'},
                                        success:function(response, options)
                                        {
                                            grid.getStore().reload();
                                            json = xt.decode(response.responseText);
                                            xAlert(json.msg);
                                        }
                                    });
                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        },

        makeForm: function(opts)
        {
            return formMaker({
                title: opts.title,
                url: action('CMS/add_or_edit_category/json'),
                fileUpload: true,
                height:140,
                width:260,
                store: this.store,
                items:[
                    {
                        name:'area',
                        value:opts.vals.area || '',
                        xtype:'hidden'
                    },
                    {
                        name:'id',
                        value: opts.vals.id || '',
                        xtype:'hidden'
                    },
                    {
                        id:'name',
                        name:'name',
                        fieldLabel:'Nome',
                        value: opts.vals.name || '',
                        xtype:'textfield',
                        width:225
                    }
                ]
            });
        }
    });
}

