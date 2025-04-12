if(!toolkit.web.cms.Permissions)
{
    toolkit.web.cms.Permissions = Ext.extend(Ext.Window, {
        constructor: function(area, permissions)
        {
            this.area = area;
            this.permissions = permissions;
            var options = {
                title:'Permissões de acesso',
                modal:true,
                width:420,
                height:350,
                layout:'fit',
                defaults:{margins:'2 2 2 2'}
            };

            toolkit.web.cms.Permissions.superclass.constructor.call(this, options);

            this.store = new xJsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'username', 'fullname', 'email'],
                proxy: new xt.data.HttpProxy({
                    method:'GET',
                    url: action('CMS/get_related_users/json')
                }),
                baseParams:{ start:0, limit:20, area:this.area },
                scope:this,
                listeners:{
                    load:function()
                    { xt.select('.athenas-delete').set({src:icons+'delete.png'}); },
                    scope:this
                }
            });
            new xt.LoadMask(xt.getBody(), {msg:'Por favor aguarde...', store:this.store});
            this.add(this.getRelatedUsers());
            this.doLayout();
        },

        getRelatedUsers: function()
        {
            if(!this.related_users)
            {
                this.related_users = new xGrid({
                    scope:this,
                    store:this.store,
                    tbar: (this.permissions.is_superuser) ?
                    [
                        {
                            tooltip:'Adicionar usuários',
                            icon: icons+'add.png',
                            text: 'Adicionar',
                            handler: function()
                            { this.makeRelateUserForm({title:'Adicionar Usuário', vals:{area:this.area}}).show(); },
                            scope:this
                        },
                        '-',
                        {
                            tooltip:'Aplicar às Áreas',
                            icon: icons+'apply-on-areas.png',
                            text: 'Aplicar às Áreas',
                            handler: function()
                            {
                                var users = []
                                this.store.each(
                                    function()
                                    { users[users.length] = this.get('id'); }
                                );
                                users = users.join(',');

                                xAjax.request({
                                    url:action('CMS/create_permissions/json'),
                                    params: {area:this.area, users:users, profile:'adm'},
                                    success:function(response, options)
                                    {
                                        json = xt.decode(response.responseText);
                                        xAlert(json.msg);
                                    }
                                });
                            },
                            scope:this
                        }
                    ] : null,
                    columns:
                    [
                        {dataIndex:'fullname', header:'Usuário', width:200},
                        {dataIndex:'email', header:'Email', width:170},
                        {
                            xtype: 'actioncolumn',
                            width: 30,
                            scope:this,
                            items: [
                                {
                                    tooltip: 'Excluir',
                                    getClass: function(v, meta, rec, a, b)
                                    { return (this.permissions.is_superuser) ? 'athenas-delete' : ''; },
                                    handler: function(grid, row, col)
                                    {
                                        var rec = grid.getStore().getAt(row);
                                        var rel_id = this.area;
                                        xConfirm({
                                            title:'Confirmação',
                                            msg:'Confirma a remoção do usuário: '+ rec.get('fullname') +' ?',
                                            fn: function(btn)
                                            {
                                                deleteItem({
                                                    signal: btn,
                                                    model: 'User',
                                                    rel_id:rel_id,
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
                    ],
                    bbar: new Ext.PagingToolbar({
                        store: this.store,
                        displayInfo: true,
                        pageSize: 20,
                        prependButtons: true
                    })
                });
            }
            return this.related_users;
        },

        makeRelateUserForm: function(opts)
        {
            return formMaker({
                title: 'Adicionar Usário',
                url: action('CMS/relate_user/json'),
                width:300,
                height:150,
                store: this.store,
                items:[
                    {
                        id:'area',
                        name:'area',
                        value: opts.vals.area || '',
                        xtype:'hidden'
                    },
                    {
                        id:'combo-users',
                        xtype:'combo',
                        width:270,
                        scope:this,
                        triggerAction: 'all',
                        lazyRender:true,
                        valueField: 'id',
                        displayField: 'fullname',
                        fieldLabel:'Digite o nome do servidor',
                        hiddenName:'user',
                        store: new xJsonStore({
                            root: 'result',
                            totalProperty: 'total',
                            remoteSort: true,
                            fields: ['id', 'fullname'],
                            url: action('CMS/get_users/json')
                        })
                    }
                ]
            });
        }

    });
}

