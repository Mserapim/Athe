Ext.ns('toolkit.common.mailing');
//var icons = '/'+CONTEXT+'/static/common/icons/';
toolkit.common.icons = '/'+CONTEXT+'/static/common/icons/';
toolkit.common.mailing.delete = function(opts)
{
    Ext.Msg.confirm(
        'Confirmação',
        opts.message,
        function(btn)
        {
            if(btn == 'yes')
            {
                Ext.Ajax.request({
                    url: action(opts.controller+'/delete/json'),
                    params: { id: opts.id },
                    success: function(response)
                    {
                        var json = Ext.decode(response.responseText);
                        if( json.success )
                            opts.store.reload();
                        else
                            Ext.Msg.alert('Erro', json.msg);
                    }
                });
            }
        }
    );
}

toolkit.common.mailing.Commons = Ext.extend(Ext.Window, {
    controller: 'MailingCommon',
    name: 'common',
    namePlural: 'commons',
    genre: 'o',
    genrePlural: 'os',
    storeFields: ['id', 'name', 'slug'],
    extraStoreFields: [],
    extraStoreParams: {},
    storeUrlEndpoint: '/all/json',
    formUrlEndpoint: '/add_or_edit/json',
    formFields: [{name: 'id', xtype: 'hidden'}, {name: 'name', fieldLabel: 'Nome', width: 350, xtype: 'textfield'}],
    gridColumns: [
        {dataIndex:'name', header:'Nome', width:300, renderer: function(name){
            return toolkit.util.replaceAll(name, '\\', '');
        }}
    ],
    actionButtons: {edit: true, delete: true},

    constructor: function(config)
    {
        config = config || {};
        toolkit.common.mailing.Commons.superclass.constructor.call(this,
            Ext.apply({
                title: 'Commons',
                closable: true,
                height: 350,
                width: 400,
                modal: true,
                layout: 'border',
                tbar: this._getTopBar(),
                items: this._getGrid(),
                bbar: this._getPagination()
            }, config)
        );


    },

    _getTopBar: function()
    {
        return [
            {
                tooltip: 'Nov'+ this.genre +' '+ this.name,
                icon: toolkit.common.icons+'add.png',
                text: 'Nov'+ this.genre,
                handler: function()
                {
                    this._makeForm({
                        title: 'Nov'+ this.genre +' '+ this.name,
                        store: this._getStore()
                    }).show();
                },
                scope: this
            }
        ];
    },

    _getStore: function()
    {
        if(!this._store)
        {
            this._store = new Ext.data.JsonStore({
                scope: this,
                autoLoad: true,
                baseParams: Ext.apply({ start:0, limit:30 }, this.extraStoreParams),
                root: 'result',
                totalProperty: 'total',
                fields: this.storeFields.concat(this.extraStoreFields),
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action(this.controller+this.storeUrlEndpoint)
                }),
                listeners: {
                    load: function()
                    {
                        Ext.select('.mailing-adm').set({src:toolkit.common.icons+'adm.png'});
                        Ext.select('.mailing-basic').set({src:toolkit.common.icons+'basic.png'});
                    }
                }
            });
        }
        return this._store;
    },

    _getPagination: function()
    {
        if(!this._pagination)
        {
            this._pagination = new Ext.PagingToolbar({
                store: this._getStore(),
                displayInfo: true,
                pageSize: 30,
                prependButtons: true
            });
        }
        return this._pagination;
    },

    _getGridColumns: function()
    { return this.gridColumns.concat([this._getActionColumn()]); },

    _getActionColumn: function()
    {
        return {
            xtype: 'actioncolumn',
            header: 'Controles',
            width: 80,
            items: this._getActions()
        };
    },

    _getActions: function()
    {
        var actions = [];
        if(this.actionButtons.edit)
        {
            actions[actions.length] = {
                tooltip: 'Editar ou visualizar '+this.name,
                icon: toolkit.common.icons+'edit.png',
                handler: function(grid, row, col)
                {
                   this._makeForm({
                        title: 'Editar '+this.name,
                        record: grid.getStore().getAt(row)
                    }).show();
                },
                scope: this
            }
        }
        if(this.actionButtons.delete)
        {
            actions[actions.length] = {
                tooltip: 'Excluir '+this.name,
                icon: toolkit.common.icons+'delete.png',
                handler: function(grid, row, col)
                {
                    var record = grid.getStore().getAt(row);
                    toolkit.common.mailing.delete({
                        id: record.get('id'),
                        controller: this.controller,
                        store: grid.getStore(),
                        message: 'Confirma exclusão d' +this.genre+ ' '+ this.name +' "'+ record.get('name') +'" ?'
                    });
                },
                scope: this
            }
        }
        return actions;
    },

    _getGrid: function()
    {
        if(!this._grid)
        {
            this._grid = new Ext.grid.GridPanel({
                scope: this,
                store: this._getStore(),
                region: 'center',
                columns: this._getGridColumns()
            });
        }
        return this._grid
    },

    _makeFormFields: function(record)
    {
        var fields = [];
        Ext.each(this.formFields, function(item){
            field = Ext.apply({value: ''}, item);
            field.value = item.value || (record) ? record.data[item.name] : '';

            if(Ext.isString(field.value))
                field.value = toolkit.util.replaceAll(field.value, '\\', '');

            fields[fields.length] = field;
        });
        return fields;
    },

    _makeForm: function(opts)
    {
        opts = opts || {}
        opts = Ext.apply({
            title: 'Nov'+ this.genre +' '+ this.name,
            store: this._getStore(),
            success: null
        }, opts);

        return new ExtFormHelper({
            url: action(this.controller+this.formUrlEndpoint),
            store: opts.store,
            success: opts.success,
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                autoWidth: true,
                autoHeight: true,
                items: this._makeFormFields(opts.record)
            }
        });
    }

});

toolkit.common.mailing.Profiles = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingProfile',
    name: 'grupo de trabalho',
    namePlural: 'grupos de trabalho',
    extraStoreFields: ['printer_name'],

    constructor: function()
    {
        toolkit.common.mailing.Profiles.superclass.constructor.call(this, {
            id: 'mailing-profiles',
            title: 'Grupos de Trabalho'
        });

        this.formFields = this.formFields.concat([{
            xtype: 'textfield',
            name: 'printer_name',
            fieldLabel: 'Nome da impressora de etiquetas',
            width: 350
        }]);
    },

    _getActions: function()
    {
        return [
            {
                tooltip: 'Usuários do '+this.name,
                icon: toolkit.common.icons+'add.png',
                handler: function(grid, row, col)
                {
                    var record = grid.getStore().getAt(row);
                    new toolkit.common.mailing.ProfileUsers(record.get('id')).show();
                },
                scope: this
            }
        ].concat(toolkit.common.mailing.Profiles.superclass._getActions.call(this));
    }
});

toolkit.common.mailing.ProfileUsers = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingProfileUsers',
    name: 'usuário',
    namePlural: 'usuários',
    storeUrlEndpoint: '/get/json',
    formUrlEndpoint: '/add_user/json',
    toggleAdminUser: '/toggle_admin_user/json',
    extraStoreFields: ['fullname', 'permission', 'permission_name'],
    gridColumns: [{dataIndex:'fullname', header:'Nome', width:300}],
    actionButtons: {delete: true},

    constructor: function(profile)
    {
        this.profile = profile;
        this.extraStoreParams = {profile: this.profile};
        toolkit.common.mailing.ProfileUsers.superclass.constructor.call(this, {
            id: 'mailing-users',
            title: 'Usuário do grupo de trabalho'
        });
    },

    _getActions: function()
    {
        return [
            {
                tooltip: 'Alterar',
                // getClass: function(v, meta, rec, a, b)
                // { return rec.get('permission') ? 'mailing-adm' : 'mailing-basic'; },
                icon: toolkit.common.icons+'edit.png',
                handler: function(grid, row, col)
                {
                    var record = grid.getStore().getAt(row);
                    this._makeForm({
                        title: 'Alterar usuário',
                        record: record
                    }).show();

                    // Ext.Ajax.request({
                    //     url: action(this.controller+this.toggleAdminUser),
                    //     params: {user: record.get('id'), permission: record.get('permission') ? false : true},
                    //     success: function(response)
                    //     {
                    //         var json = Ext.decode(response.responseText);
                    //         if(json.success)
                    //             grid.getStore().reload();
                    //         else
                    //             Ext.Msg.alert('Erro', json.msg);
                    //     }
                    // });
                },
                scope: this
            },
            {
                tooltip: 'Excluir '+this.name,
                icon: toolkit.common.icons+'delete.png',
                handler: function(grid, row, col)
                {
                    var record = grid.getStore().getAt(row);
                    var controller = this.controller;
                    var profile = this.profile;
                    Ext.Msg.confirm(
                        'Confirmação',
                        'Confirma exclusão d' +this.genre+ ' '+ this.name +' "'+ record.get('fullname') +'" ?',
                        function(btn)
                        {
                            if(btn == 'yes')
                            {
                                Ext.Ajax.request({
                                    url: action(controller+'/remove_user/json'),
                                    params: { user: record.get('id'), profile: profile },
                                    success: function(response)
                                    {
                                        var json = Ext.decode(response.responseText);
                                        if( json.success )
                                            grid.getStore().reload();
                                        else
                                            Ext.Msg.alert('Erro', json.msg);
                                    }
                                });
                            }
                        }
                    );
                },
                scope: this
            }
        ]
    },

    _makeFormFields: function(record)
    {
        return [
            {
                xtype: 'hidden',
                name: 'profile',
                value: this.profile
            },
            {
                xtype: 'combo',
                width: 270,
                scope: this,
                typeAhead: true,
                triggerAction: 'all',
                lazyRender: true,
                valueField: 'id',
                displayField: 'fullname',
                fieldLabel: 'Digite o nome do servidor',
                hiddenName: 'user',
                hiddenValue: (record) ? record.get('id') : '',
                name: 'display_name',
                value: (record) ? record.get('fullname') : '',
                store: new Ext.data.JsonStore({
                    root: 'result',
                    fields: ['id', 'fullname'],
                    url: action(this.controller+'/users/json')
                })
            },
            {
                xtype: 'combo',
                width: 270,
                scope: this,
                triggerAction: 'all',
                mode: 'local',
                valueField: 'perm',
                displayField: 'name',
                hiddenName: 'permission',
                hiddenValue: (record) ? record.get('permission') : 'basic',
                value: (record) ? record.get('permission_name') : 'Básico',
                store: new Ext.data.ArrayStore({
                    fields: ['perm', 'name'],
                    data: [['basic', 'Básico'], ['reviser', 'Revisor'], ['admin', 'Adiministrador']]
                })
            }
        ];
    }
});

toolkit.common.mailing.Treatments = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingTreatment',
    name: 'pronome de tratamento',
    namePlural: 'pronomes de tratamento',

    constructor: function()
    {
        toolkit.common.mailing.Treatments.superclass.constructor.call(this, {
            id: 'mailing-treatments',
            title: 'Pronomes de Tratamento'
        });
    }
});

toolkit.common.mailing.Positions = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingPosition',
    name: 'cargo',
    namePlural: 'cargos',

    constructor: function()
    {
        toolkit.common.mailing.Positions.superclass.constructor.call(this, {
            id: 'mailing-positions',
            title: 'Cargos'
        });
    }
});

toolkit.common.mailing.Companies = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingCompany',
    name: 'órgão',
    namePlural: 'órgãos',

    constructor: function()
    {
        toolkit.common.mailing.Companies.superclass.constructor.call(this, {
            id: 'mailing-companies',
            title: 'Órgãos'
        });
    }
});

toolkit.common.mailing.States = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingState',
    name: 'estado',
    namePlural: 'estados',

    constructor: function()
    {
        this.extraStoreFields = ['UF'];
        this.formFields = this.formFields.concat([{
            id: 'UF',
            fieldLabel: 'UF',
            name: 'UF',
            width: 30,
            xtype: 'textfield'
        }]);

        toolkit.common.mailing.Cities.superclass.constructor.call(this, {
            id: 'mailing-states',
            title: 'Estados'
        });
    }
});

toolkit.common.mailing.Cities = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingCity',
    name: 'cidade',
    namePlural: 'cidades',
    genre: 'a',
    genrePlural: 'as',

    constructor: function()
    {
        this.extraStoreFields = ['state_id', 'state'];
        this.gridColumns = [
            {dataIndex:'name', header:'Nome', width:170, renderer: function(name){
                return toolkit.util.replaceAll(name, '\\', '');
            }},
            {dataIndex:'state', header:'Estado', width:130}
        ];
        toolkit.common.mailing.Cities.superclass.constructor.call(this, {
            id: 'mailing-cities',
            title: 'Cidades'
        });
    },

    _makeFormFields: function(record)
    {
        var fields = toolkit.common.mailing.Cities.superclass._makeFormFields.call(this, record);

        var combo = new Ext.form.ComboBox({
            xtype: 'combo',
            hiddenName: 'state',
            fieldLabel: 'Estado',
            hiddenValue: (record) ? record.get('state_id') : '',
            value: (record) ? record.get('state') : '',
            mode: 'local',
            triggerAction: 'all',
            width: 320,
            valueField: 'id',
            displayField: 'name',
            store: new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'name'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('MailingState/all/json')
                })
            })
        });

        var addButton = {
            xtype: 'button',
            icon: toolkit.common.icons+'add.png',
            handler: function()
            {
                new toolkit.common.mailing.States()._makeForm({
                    store: combo.getStore(),
                    success: function(form, action)
                    {
                        combo.getStore().on('load', function(){
                            combo.setValue(action.result.data);
                        });
                    }
                }).show();
            }
        };

        return fields.concat([{
            layout: 'column',
            border: false,
            items: [
                {
                    layout: 'form',
                    border: false,
                    items: [combo]
                },
                {
                    layout: 'form',
                    bodyStyle: 'margin: 19px 0 0 7px;',
                    border: false,
                    items: [addButton]
                }
            ]
        }]);
    }
});

toolkit.common.mailing.Groups = Ext.extend(toolkit.common.mailing.Commons, {
    controller: 'MailingGroup',
    name: 'grupo de contatos',
    namePlural: 'grupos de contatos',

    constructor: function(profile, fakeItem, limit)
    {
        this.profile = profile;
        this.extraStoreParams = {profile: this.profile, fakeItem: fakeItem || 0, limit: limit || 30};
        toolkit.common.mailing.Groups.superclass.constructor.call(this, {
            id: 'mailing-groups',
            title: 'Grupo de contatos'
        });
    },

    _makeFormFields: function(record)
    {
        var fields = toolkit.common.mailing.Groups.superclass._makeFormFields.call(this, record);
        return fields.concat([{
            xtype: 'hidden',
            name: 'profile',
            value: this.profile
        }]);
    }
});


toolkit.common.mailing.Contacts = Ext.extend(Ext.Panel, {
    constructor: function(profile, permission)
    {
        this.profile = profile;
        this.permission = permission;
        var config = {
            id: 'mailing-contacts',
            title: 'Contatos',
            closable: true,
            layout: 'fit',
        };

        if(this.profile)
        {
            var menu = [
                '->',
                {
                    tooltip: 'Imprimir',
                    icon: toolkit.common.icons+'print.png',
                    text: 'Imprimir',
                    handler: function()
                    { this._getPrintWindow().show() },
                    scope: this
                },
                '-',
                {
                    id: 'search-keyword',
                    xtype: 'textfield',
                    emptyText: 'palavra-chave...'
                },
                {
                    tooltip: 'Pesquisar por nome de contato',
                    text: 'Pesquisar',
                    handler: function()
                    {

                        var keyword = Ext.getCmp('search-keyword').getValue();
                        if(Ext.isEmpty(keyword) || keyword.length > 3)
                            this._getStore().reload({params: {search: keyword}})
                        else
                            Ext.Msg.alert('Aviso', 'Digite pelo menos 4 caracteres para realizar a pesquisa.');
                    },
                    scope:this
                },
                {
                    tooltip: 'Todos os contatos',
                    text: 'Recuperar todos',
                    handler: function()
                    { this._getStore().load() },
                    scope: this
                }
            ];

            if(permission == 'admin')
            {
                var adminMenu = [
                    '-',
                    {
                        tooltip: 'Pronomes de tratamento',
                        text: 'Pronomes',
                        handler: function()
                        { new toolkit.common.mailing.Treatments().show() },
                        scope:this
                    },
                    {
                        tooltip: 'Órgãos',
                        text: 'Órgãos',
                        handler: function()
                        { new toolkit.common.mailing.Companies().show() },
                        scope:this
                    },
                    {
                        tooltip: 'Cargos',
                        text: 'Cargos',
                        handler: function()
                        { new toolkit.common.mailing.Positions().show() },
                        scope:this
                    },
                    {
                        tooltip: 'Cidades',
                        text: 'Cidades',
                        handler: function()
                        { new toolkit.common.mailing.Cities().show() },
                        scope:this
                    },
                    {
                        tooltip: 'Estados',
                        text: 'Estados',
                        handler: function()
                        { new toolkit.common.mailing.States().show() },
                        scope:this
                    },
                    {
                        tooltip: 'Grupos de contatos',
                        text: 'Grupos',
                        handler: function()
                        { new toolkit.common.mailing.Groups(this.profile).show() },
                        scope:this
                    }
                ];
                menu = adminMenu.concat(menu);
            }

            if(permission == 'reviser' || permission == 'admin')
            {
                menu.unshift({
                    tooltip: 'Novo contato',
                    icon: toolkit.common.icons+'add.png',
                    text: 'Novo',
                    handler: function()
                    { this._makeForm({title: 'Novo contato', vals: {profile: this.profile}}).show(); },
                    scope: this
                });
            }

            config = Ext.apply(config, {
                tbar: menu,
                items: [this._getGrid()],
                bbar: [this._getPagination()]
            });

            new Ext.LoadMask(toolkit.Application.tabspace.getEl(), {msg:'Aguarde...', store: this._getStore()});
        }
        else
        {
            config = Ext.apply(config, {
                listeners: {
                    show: function()
                    {
                        Ext.Msg.alert('Aviso', 'Você não pertence a nenhum grupo de utilização de mala de direta.\n' +
                            'Entre em contato com o Departamento de Desenvolvimento de Software.');
                    }
                }
            });
        }

        var cmp = Ext.getCmp('mailing-contacts');
        if(!cmp)
        {
            toolkit.common.mailing.Contacts.superclass.constructor.call(this, config);
            toolkit.Application.tabspace.add(this);
        }
        else
            return cmp;

    },

    _getStore: function()
    {
        if(!this._store)
        {
            this._store = new Ext.data.JsonStore({
                scope: this,
                autoLoad: true,
                baseParams: {start: 0, limit :30, profile: this.profile, search: ''},
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'name', 'slug', 'profile_id', 'groups', 'company', 'company_id',
                'position', 'position_id', 'treatment', 'treatment_id', 'locality', 'neighborhood',
                'code', 'city', 'city_id', 'normal', 'fax', 'mobile', 'group_id', 'group'],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: action('MailingContact/get/json')
                })
            });
        }
        return this._store;
    },

    _getPagination: function()
    {
        if(!this._pagination)
        {
            this._pagination = new Ext.PagingToolbar({
                store: this._getStore(),
                displayInfo: true,
                pageSize: 30,
                prependButtons: true
            });
        }
        return this._pagination;
    },

    _getGrid: function()
    {
        if(!this._grid)
        {
            var columns = [
                {dataIndex:'treatment', header:'Pronome de tratamento', width:150},
                {dataIndex:'name', header:'Nome', width:200},
                {dataIndex:'position', header:'Cargo', width:150},
                {dataIndex:'company', header:'Órgão', width:250},
                {dataIndex:'groups', header:'Grupos', width:100, renderer: function(list) {
                    var lis = [];
                    Ext.each(list, function(item){ lis[lis.length] = { tag:'li', html: item.name }; });
                    return Ext.DomHelper.markup({ tag: 'ul', children: lis});
                }}
            ];

            if(this.permission == 'admin' || this.permission == 'reviser')
            {
                columns = columns.concat(
                    [
                        {
                            xtype: 'actioncolumn',
                            header:'Controles',
                            width: 60,
                            scope: this,
                            items:
                            [
                                {
                                    tooltip:'Editar ou visualizar contato',
                                    icon: toolkit.common.icons+'edit.png',
                                    handler: function(grid, row, col)
                                    {
                                        var record = grid.getStore().getAt(row)
                                        this._makeForm({
                                            title: 'Editar votação',
                                            vals: {
                                                profile: this.profile,
                                                id: record.get('id'),
                                                name: toolkit.util.replaceAll(record.get('name'), '\\', ''),
                                                slug: record.get('slug'),
                                                profile_id: record.get('profile_id'),
                                                company: toolkit.util.replaceAll(record.get('company'), '\\', ''),
                                                company_id: record.get('company_id'),
                                                position: record.get('position'),
                                                position_id: record.get('position_id'),
                                                treatment: record.get('treatment'),
                                                treatment_id: record.get('treatment_id'),
                                                locality: toolkit.util.replaceAll(record.get('locality'), '\\', ''),
                                                neighborhood: record.get('neighborhood'),
                                                code: record.get('code'),
                                                city: toolkit.util.replaceAll(record.get('city'), '\\', ''),
                                                city_id: record.get('city_id'),
                                                normal: record.get('normal'),
                                                fax: record.get('fax'),
                                                mobile: record.get('mobile'),
                                                group_id: record.get('group_id'),
                                                group: record.get('group')
                                            }
                                        }).show();
                                    },
                                    scope:this
                                },
                                {
                                    tooltip: 'Excluir contato',
                                    icon: toolkit.common.icons+'delete.png',
                                    handler: function(grid, row, col)
                                    {
                                        var record = grid.getStore().getAt(row);
                                        toolkit.common.mailing.delete({
                                            id: record.get('id'),
                                            controller: 'MailingContact',
                                            store: grid.getStore(),
                                            message: 'Confirma exclusão do contato "'+ record.get('name') +'" ?'
                                        });
                                    },
                                    scope:this
                                }
                            ]
                        }
                    ]
                );
            }

            this._grid = new Ext.grid.GridPanel({
                scope:this,
                store: this._getStore(),
                region:'center',
                columns: columns
            });
        }
        return this._grid
    },

    _getPrintWindow: function()
    {
        var positions = [], tags = [], i;
        for(i=1; i<=14; i++)
        {
            positions[positions.length] = 1;
            tags[tags.length] = new Ext.Button({
                text: 'etiqueta '+ i,
                width: 130,
                enableToggle: true,
                pressed: true,
                toggleHandler: function(button, clicked)
                { positions[tags.indexOf(button)] = (!clicked) ? 0 : 1; }
            });
        }
        var store = new toolkit.common.mailing.Groups(this.profile, 1, 200)._getStore();
        //store.load({params: {limit: 200}});
        var formPanel = new Ext.FormPanel({
            labelAlign: 'top',
            border: false,
            width: 350,
            autoHeight: true,
            bodyStyle: 'padding:10px;',
            items: [
                {
                    xtype: 'combo',
                    fieldLabel: 'Imprimir',
                    hiddenName: 'group',
                    hiddenValue: 0,
                    value: 'Todos os selecionados',
                    mode: 'local',
                    triggerAction: 'all',
                    width: 320,
                    valueField: 'id',
                    displayField: 'name',
                    store: store
                },
                {
                    xtype: "combo",
                    allowBlank: false,
                    fieldLabel: "Tamanho do Papel",
                    width: 320,
                    hiddenName: "type_paper",
                    mode: "local",
                    hiddenValue: 1,
                    value: "CARTA",
                    triggerAction: "all",
                    store: new Ext.data.ArrayStore({
                        fields: ['val', 'text'],
                        data: [
                            [1, "CARTA"],
                            [2, "A4"],
                            [3, "Rolo de etiquetas"]
                        ]
                    }),
                    valueField: 'val',
                    displayField: 'text',
                    listeners: {
                        select: function(combo, record)
                        {
                            var val = record.get('val'),
                                btn = formPanel.ownerCt.buttons[0],
                                text = (val > 2) ? 'Imprimir' : 'Gerar visualização';

                            btn.setText(text);
                        }
                    }
                },
                {
                    xtype: 'fieldset',
                    layout: 'column',
                    title: 'Posições de impressão',
                    columnWidth: .5,
                    height: 190,
                    items: [
                        {
                            layout: 'form',
                            border: false,
                            bodyStyle: 'margin: 0 10px;',
                            items: tags.slice(0, 7)
                        },
                        {
                            layout: 'form',
                            border: false,
                            bodyStyle: 'margin: 0 10px;',
                            items: tags.slice(7)
                        }
                    ]
                }
            ]
        });
        var print = new Ext.Window({
            title: 'Impressão de etiquetas',
            frame: true,
            modal: true,
            width: 365,
            tbar: [
                {
                    scope: this,
                    text: 'Sobre a impressão',
                    handler: function()
                    {
                        new Ext.Window({
                            title: 'Instruções de impressão',
                            modal: true,
                            html: '<div style="padding:10px;">' +
                                '<ol>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Na opção "Imprimir" selecione a categoria de contatos que deseja imprimir</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Clique em gerar visualização</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Abrar o arquivo PDF gerado</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Tecle CTRL+P</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Clique na aba manuseio de página</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Na opção "Escala" selecione "Nenhum"</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Desmarque a opção "Auto rotacionar e centralizar"</li>' +
                                    '<li style="list-style: decimal inside; margin: 5px 0;">Clique em imprimir</li>' +
                                '</ol>' +
                            '</div>'
                        }).show();
                    }
                }
            ],
            items: [ formPanel ],
            buttons: [
                {
                    scope: this,
                    text: 'Gerar visualização',
                    handler: function()
                    {

                        var val = formPanel.items.get(0).getValue();
                        var selections = this._getGrid().getSelectionModel().getSelections();
                        var paperType = formPanel.items.get(1).getValue()
                        if( (val == 'Todos os selecionados' && selections.length > 0) || val != 'Todos os selecionados')
                        {
                            var loading = new Ext.LoadMask(formPanel.getEl(), {msg: 'Agurade a geração das etiquetas para impressao'});
                            loading.show();
                            var selected = [];
                            Ext.each(selections, function(item) {
                                selected[selected.length] = item.get('id');
                            });

                            // var url = 'MailingContact/print_tags/json';
                            // if (paperType == 3)
                            //     url += '?roll=1';

                            formPanel.getForm().submit({
                                scope:this,
                                url: action('MailingContact/print_tags/json'),
                                params: {
                                    selected: selected.join(),
                                    positions: positions.join(),
                                    profile: this.profile
                                },
                                success: function(form, action)
                                {
                                    if (paperType != 3)
                                    {
                                        var paperTypeReport = {
                                            1: {paper: 'carta' ,report:'/to/mpe/maladireta/carta/catorze'},
                                            2: {paper: 'a4' ,report:'/to/mpe/maladireta/a4/catorze'}
                                        };

                                        var reportDef = paperTypeReport[1];
                                        if (paperType && Number.isInteger(paperType))
                                            reportDef = paperTypeReport[paperType]

                                       engine.mq.Report.request({
                                            report: reportDef.report,
                                            params: {
                                                profile: this.profile,
                                                id: action.result.data,
                                                outfile: 'etiquetas-' + reportDef.paper,
                                                report_name: 'Etiquetas ' + reportDef.paper
                                            },
                                            el: this.getEl(),
                                            waitMessage: 'Gerando relatório...',
                                        });
                                        print.destroy()
                                    }
                                    loading.hide();
                                },
                                failure: function(form, action)
                                {
                                    loading.hide();
                                    switch (action.failureType)
                                    {
                                        case Ext.form.Action.CONNECT_FAILURE:
                                            Ext.Msg.alert('Falha', 'A comunicação com servidor falhou!');
                                            break;
                                        case Ext.form.Action.SERVER_INVALID:
                                            Ext.Msg.alert('Falha', action.result.msg);
                                   }
                                }
                            });
                        }
                        else
                            Ext.Msg.alert('Falha', 'Selecione pelo menos uma etiqueta ou um grupo de etiquetas para realizar a impressão.')
                    },
                }
            ]
        });
        return print;
    },

    _makeForm: function(opts)
    {
        var createCombo = function(label, name, value, displayValue, url, buttonCallback, displayField)
        {
            var displayField = displayField || 'name';
            var store = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                baseParams: {profile: opts.vals.profile},
                fields: ['id', displayField],
                proxy: new Ext.data.HttpProxy({
                    method: 'GET',
                    url: url
                }),
                listeners: {
                    load: function(store, records)
                    {
                        Ext.each(records, function(record){
                            record.set(displayField, toolkit.util.replaceAll(record.get(displayField), '\\', ''));
                            record.commit();
                        });
                    }
                }
            });
            var combo = new Ext.form.ComboBox({
                fieldLabel: label,
                hiddenName: name,
                hiddenValue: value || '',
                value: displayValue || '',
                mode: 'local',
                triggerAction: 'all',
                width: 320,
                valueField: 'id',
                displayField: displayField,
                store: store
            });

            var addButton = {
                xtype: 'button',
                icon: toolkit.common.icons+'add.png',
                handler: function() { buttonCallback(combo); }
            };

            return {
                layout: 'column',
                border: false,
                items: [
                    {
                        layout: 'form',
                        border: false,
                        items: [combo]
                    },
                    {
                        layout: 'form',
                        bodyStyle: 'margin: 19px 0 0 7px;',
                        border: false,
                        items: [addButton]
                    }
                ]
            };
        }

        return new ExtFormHelper({
            url: action('MailingContact/add_or_edit/json'),
            store: this._getStore(),
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                width: 390,
                height: 490,
                autoScroll: true,
                items: [
                    {
                        name: 'profile',
                        value: opts.vals.profile || '',
                        xtype: 'hidden'
                    },
                    {
                        name: 'id',
                        value: opts.vals.id || '',
                        xtype: 'hidden'
                    },
                    {
                        name: 'name',
                        fieldLabel: 'Nome',
                        value: opts.vals.name || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    createCombo(
                        'Pronome de tratamento',
                        'treatment',
                        opts.vals.treatment_id,
                        opts.vals.treatment,
                        action('MailingTreatment/all/json'),
                        function(combo)
                        {
                            new toolkit.common.mailing.Treatments()._makeForm({
                                store: combo.getStore(),
                                success: function(form, action)
                                {
                                    combo.getStore().on('load', function(){
                                        combo.setValue(action.result.data);
                                    });
                                }
                            }).show()
                        }
                    ),
                    createCombo(
                        'Cargo',
                        'position',
                        opts.vals.position_id,
                        opts.vals.position,
                        action('MailingPosition/all/json'),
                        function(combo)
                        {
                            new toolkit.common.mailing.Positions()._makeForm({
                                store: combo.getStore(),
                                success: function(form, action)
                                {
                                    combo.getStore().on('load', function(){
                                        combo.setValue(action.result.data);
                                    });
                                }
                            }).show();
                        }
                    ),
                    createCombo(
                        'Órgão',
                        'company',
                        opts.vals.company_id,
                        opts.vals.company,
                        action('MailingCompany/all/json'),
                        function(combo)
                        {
                            new toolkit.common.mailing.Companies()._makeForm({
                                store: combo.getStore(),
                                success: function(form, action)
                                {
                                    combo.getStore().on('load', function(){
                                        combo.setValue(action.result.data);
                                    });
                                }
                            }).show();
                        }
                    ),
                    {
                        name: 'locality',
                        fieldLabel: 'Endereço',
                        value: opts.vals.locality || '',
                        width: 350,
                        xtype:'textfield'
                    },
                    {
                        name: 'neighborhood',
                        fieldLabel: 'Bairro',
                        value: opts.vals.neighborhood || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    createCombo(
                        'Cidade',
                        'city',
                        opts.vals.city_id,
                        opts.vals.city,
                        action('MailingCity/all/json'),
                        function(combo)
                        {
                            new toolkit.common.mailing.Cities()._makeForm({
                                store: combo.getStore(),
                                success: function(form, action)
                                {
                                    combo.getStore().on('load', function(){
                                        combo.setValue(action.result.data);
                                    });
                                }
                            }).show();
                        },
                        'fullname'
                    ),
                    {
                        name: 'code',
                        fieldLabel: 'CEP',
                        value: opts.vals.code || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    {
                        name: 'normal',
                        fieldLabel: 'Telefone principal',
                        value: opts.vals.normal || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    {
                        name: 'fax',
                        fieldLabel: 'Fax',
                        value: opts.vals.fax || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    {
                        name: 'mobile',
                        fieldLabel: 'Celular',
                        value: opts.vals.mobile || '',
                        width: 350,
                        xtype: 'textfield'
                    },
                    createCombo(
                        'Grupo',
                        'group',
                        opts.vals.group_id,
                        opts.vals.group,
                        action('MailingGroup/all/json'),
                        function(combo)
                        {
                            new toolkit.common.mailing.Groups(opts.vals.profile)._makeForm({
                                store: combo.getStore(),
                                success: function(form, action)
                                {
                                    combo.getStore().on('load', function(){
                                        combo.setValue(action.result.data);
                                    });
                                }
                            }).show();
                        }
                    )
                ]
            }
        });
    }
});
