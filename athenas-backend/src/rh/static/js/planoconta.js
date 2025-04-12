
Ext.ns('toolkit.gfp.planoconta');

Ext.apply(
    toolkit.gfp.planoconta,
    {
        PlanoContaRestful: Ext.extend(
            toolkit.restful.FormPanel,
            {
                router: toolkit.util.Normalize.controller_action('PCPlanoConta'),
                                      
                getFormPanel: function() {
                    if(!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            items: [
                                {
                                    xtype: 'panel',
                                    layout: 'form',
                                    items: [
                                        {
                                            xtype: 'combo',
                                            triggerAction: 'all',
                                            editable: false,
                                            fieldLabel: 'Finalidade',
                                            width: 365,
                                            store: [
                                                [1, 'LIQUIDAÇÃO'],
                                                [2, 'DESEMBOLSO']
                                            ],
                                            hiddenName: 'finalidade',
                                            value: (this.values ? this.values.finalidade : '')
                                        },
                                        {
                                            xtype: 'combo',
                                            triggerAction: 'all',
                                            editable: false,
                                            fieldLabel: 'Tipo',
                                            width: 365,
                                            store: [
                                                [1, 'ATIVO'],
                                                [2, 'INATIVO'],
                                                [3, 'PENSIONISTA']
                                            ],
                                            hiddenName: 'tipo',
                                            value: (this.values ? this.values.tipo : '')
                                        },
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Inscrição da NE',
                                            width: 365,
                                            name: 'inscricao_ne',
                                            value: (this.values ? this.values.inscricao_ne : '')
                                        }
                                    ]
                                },
                                {
                                    xtype: 'panel',
                                    layout: 'column',
                                    defaults: {
                                        columnWidth: .5,
                                        xtype: 'fieldset',
                                        layout: 'form',
                                        labelAlign: 'top',
                                        style: 'margin: 5px; padding: 2px 10px',
                                        defaults: {
                                            width: 200
                                        }
                                    },
                                    items: [
                                        {
                                            title: 'Conta de Debito',
                                            items: [
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Evento',
                                                    flex: 1.0,
                                                    name: 'evento_nld',
                                                    value: (this.values ? this.values.evento_nld : '')
                                                },
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Classificação',
                                                    flex: 1.0,
                                                    name: 'classificacao_nld',
                                                    value: (this.values ? this.values.classificacao_nld : '')
                                                }
                                            ]
                                        },
                                        {
                                            title: 'Conta de Crédito',
                                            items: [
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Evento',
                                                    name: 'evento_nlc',
                                                    value: (this.values ? this.values.evento_nlc : '')
                                                },
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Classificação',
                                                    name: 'classificacao_nlc',
                                                    value: (this.values ? this.values.classificacao_nlc : '')
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        });
                        
                    return this.formPanel
                },
                                      
                constructor: function(cf) {
                    if(!cf) cf = {};
                    
                    var df = {
                        modal: true,
                        title: 'Contas',
                        width: 500,
                        border: false
                    };
                    
                    Ext.applyIf(cf, df);
                    
                    toolkit.gfp.planoconta.PlanoContaRestful.superclass.constructor.call(this, cf);
                }
            }
        ),
        
        PlanoRestful: Ext.extend(
            toolkit.restful.FormPanel,
            {
                router: toolkit.util.Normalize.controller_action('PCPlano'),
                                 
                getFormPanel: function() {
                    console.debug(this.values);
                    
                    if(!this.formPanel) 
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            defaults: {
                                width: 410
                            },
                            items: [
                                {
                                    xtype: 'textfield',
                                    fieldLabel: 'Título',
                                    maxLength: 60,
                                    allowBlank: true,
                                    value: (this.values ? this.values.titulo : ''),
                                    name: 'titulo'
                                },
                                {
                                    xtype: 'combo',
                                    fieldLabel: 'Tipo',
                                    triggerAction: 'all',
                                    editable: false,
                                    store: [
                                        [1, 'CONSIGNAÇÃO'],
                                        [2, 'LIQUIDO'],
                                        [3, 'PATRONAL'],
                                        // [4, 'SALARIO FAMILIA'],
                                        // [5, 'AUXILIO TRANSPORTE'],
                                        // [6, 'PENSÃO ALIMENTICIA'],
                                        // [7, 'AUXÍLIO CRECHE'],
                                        // [8, 'DEP. JUDICIAL'],
                                    ],
                                    hiddenName: 'tipo',
                                    value: (this.values ? this.values.tipo : '')
                                },
                                {
                                    xtype: 'autocompletefield',
                                    fieldLabel: 'Pessoa Juridica',
                                    hiddenName: 'pessoa_juridica',
                                    hideTrigger: true,
                                    triggerAction: 'all',
                                    crudController: 'RHPessoaJuridica',
                                    queryParam: 'keyword',
                                    queryAction: 'query',
                                    displayField: 'description',
                                    valueField: 'pk',
                                    value: (this.values ? this.values.pessoa_juridica : '') 
                                },
                                {
                                    xtype: "rest-autocompletefield", 
                                    fieldLabel: "Tipo de Folha", 
                                    allowBlank: false, 
                                    rest: "rh.gfp.payroll.PayrollTypeRestful", 
                                    name: "folha_tipo",
                                    value: (this.values ? this.values.folha_tipo : '')
                                }, 
                                {
                                    xtype: 'numberfield',
                                    fieldLabel: 'Ano',
                                    name: 'ano_calendario',
                                    value: (this.values ? this.values.ano_calendario : '') 
                                },
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Banco",
                                    allowBlank: false,
                                    rest: "rh.bank.BankRestful",
                                    name: "banco",
                                    value: (this.values ? this.values.banco : '')
                                },
                                {
                                    xtype: 'textfield',
                                    fieldLabel: 'Agência',
                                    maxLength: 15,
                                    allowBlank: true,
                                    value: (this.values ? this.values.agencia : ''),
                                    name: 'agencia'
                                },
                                {
                                    xtype: 'textfield',
                                    fieldLabel: 'Conta',
                                    maxLength: 15,
                                    allowBlank: true,
                                    value: (this.values ? this.values.conta : ''),
                                    name: 'conta' 
                                },
                                {
                                    xtype: 'textfield',
                                    fieldLabel: 'Fonte',
                                    maxLength: 10,
                                    allowBlank: true,
                                    value: (this.values ? this.values.fonte : ''),
                                    name: 'fonte' 
                                },
                                {
                                    frame: true,
                                    controller: 'GFPEvento', 
                                    allowBlank: false, 
                                    fieldLabel: 'Eventos', 
                                    xtype: 'multiselectbox', 
                                    name: 'eventos', 
                                    valueField: 'pk', 
                                    conf: {canAdd: false, canEdit: false}, 
                                    model: {name: 'Evento', pkg: 'gfp'}, 
                                    displayField: 'description', 
                                    hiddenName: 'eventos',
                                    value: (this.values ? this.values.eventos : ''),
                                }
                            ]
                        })
                        
                    return this.formPanel;
                },
                
                constructor: function(cf) {
                    if(!cf) cf = {};
                    
                    var df = {
                        modal: true,
                        title: 'Plano',
                        width: 550,
                        border: false
                    };
                    
                    Ext.applyIf(cf, df);
                    
                    toolkit.gfp.planoconta.PlanoRestful.superclass.constructor.call(this, cf);
                }
            }
        ),
        
        Gestor: Ext.extend(
            Ext.Panel,
            {
                setPlano: function(plano) {
                    var sto = this.getContaPanel().getStore();
                    if(plano != null) {
                        sto.baseParams = {
                            plano: plano.get('pk')
                        };
                        
                        sto.load({});
                    } else {
                        sto.baseParams['plano'] = null;
                        sto.removeAll();
                    }
                },
        
                deleteBatchConta: function() {
                    var selections = this.getContaPanel().getSelectionModel().getSelections();
                    var pks = [];
                    
                    if(selections) {
                        Ext.each(
                            selections,
                            function(i) {
                                pks.push(i.get('pk'));
                            }
                        );
                        
                        Ext.Msg.show({
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            title: 'Removendo itens',
                            msg: 'Tem certeza que deseja remover os item(ns) selecionado(s)?',
                            scope: this,
                            fn: function(b) {
                                if(b == 'yes') {
                                    Ext.Ajax.request({
                                        url: toolkit.util.Normalize.controller_action('PCPlanoConta'),
                                        method: 'POST',
                                        params: { pks: pks },
                                        success: function() { this.getContaPanel().getStore().reload() },
                                        scope: this,
                                        headers: {
                                            'Restful-Method': 'DELETE'
                                        }
                                    });
                                }
                            }
                        });
                    }
                    else alert('Primeiro você deve selecionar os itens para serem removidos.')
                },
                
                editConta: function() {
                    var selected = this.getContaPanel().getSelectionModel().getSelected();
            
                    if(selected) {
                        new toolkit.gfp.planoconta.PlanoContaRestful({
                            method: 'PUT',
                            baseParams: { 
                                pk: selected.get('pk'),
                                plano: this.getContaPanel().getStore().baseParams.plano
                            },
                            values: {
                                finalidade: selected.get('finalidade_id'),
                                tipo: selected.get('tipo_id'),
                                inscricao_ne: selected.get('inscricao_ne'),
                                evento_nlc: selected.get('evento_nlc'),
                                evento_nld: selected.get('evento_nld'),
                                classificacao_nlc: selected.get('classificacao_nlc'),
                                classificacao_nld: selected.get('classificacao_nld')
                            },
                            scope: this,
                            callback: function() { this.getContaPanel().getStore().reload() }
                        }).show()
                    }
                    else alert('Primeiro você deve um item para edição.')
                },
                
                addConta: function() {
                    var sto = this.getContaPanel().getStore();
                    
                    new toolkit.gfp.planoconta.PlanoContaRestful({
                        baseParams: {
                            plano: sto.baseParams.plano
                        },
                        scope: this,
                        callback: function() {
                            this.getContaPanel().getStore().reload();
                        }
                    }).show()
                },
                
                copyContaTipo: function() {
                    var grid = this.getContaPanel();
                    var selected = grid.getSelectionModel().getSelected();
            
                    if(selected) {
                        new Ext.Window({
                            title: 'Transportar informações de conta',
                            modal: true,
                            border: false,
                            closable: true,
                            resizable: false,
                            width: 455,
                            buttons: [
                                {
                                    text: 'Transportar',
                                    handler: function(b) {
                                        var wnd = b.ownerCt.ownerCt;
                                        var fp = wnd.getComponent('formPanel');
                                        var form = fp.getForm();
                                        
                                        form.waitMsgTarget = fp.getEl();
                                        form.submit({
                                            url: toolkit.util.Normalize.controller_action('PCGestor', 'copy_conta_tipo'),
                                            params: {
                                                src: selected.get('pk')
                                            },
                                            success: function(action, form) {
                                                grid.getStore().reload();
                                                action.ownerCt.destroy();
                                            },
                                            failure: function(action, form) {
                                                console.debug(action, form)
                                            },
                                            waitMsg: 'Transportando informações...'
                                        });
                                    }
                                },
                                {
                                    text: 'Cancelar',
                                    handler: function(b) { b.ownerCt.ownerCt.destroy() }
                                }
                            ],
                            items: {
                                id: 'formPanel',
                                xtype: 'form',
                                frame: true,
                                width: 450,
                                items: [
                                    {
                                        xtype: 'combo',
                                        fieldLabel: 'Destino',
                                        width: 320,
                                        store: [
                                            [1, 'ATIVO'],
                                            [2, 'INATIVO'],
                                            [3, 'PENSIONISTA']
                                        ],
                                        hiddenName: 'dst',
                                    }
                                ]
                            }
                        }).show()
                    }
                    else alert('Primeiro você deve um item para ser copiado.')
                },
                
                getContaPanel: function() {
                    if(!this.contaPanel) {
                        var store = new Ext.data.JsonStore({
                            url: toolkit.util.Normalize.controller_action(
                                'PCGestor', 'list_from_plano'
                            ),
                            fields: [
                                'pk', 'inscricao_ne', 'evento_nlc', 
                                'evento_nld', 'classificacao_nlc', 
                                'classificacao_nld', 'tipo', 'tipo_id', 
                                'finalidade', 'finalidade_id'
                            ],
                            root: 'root'
                        });
                        
                        this.contaPanel = new Ext.grid.GridPanel({
                            cm: new Ext.grid.ColumnModel([
                                {
                                    id: 'status',
                                    header: '',
                                    dataIndex: 'tipo',
                                    width: 50,
                                    menuDisabled: true,
                                    renderer: toolkit.util.formatStatus
                                },
                                {
                                    header: 'Evento de Debito',
                                    dataIndex: 'evento_nld',
                                    width: 150
                                },
                                {
                                    header: 'Classificação para Debito',
                                    dataIndex: 'classificacao_nld',
                                    width: 150
                                },
                                {
                                    header: 'Inscrição NE',
                                    dataIndex: 'inscricao_ne',
                                    width: 150
                                },
                                {
                                    header: 'Evento de Crédito',
                                    dataIndex: 'evento_nlc',
                                    width: 150
                                },
                                {
                                    header: 'Classificação para Crédito',
                                    dataIndex: 'classificacao_nlc',
                                    width: 150
                                }
                            ]),
                            listeners: {
                                scope: this,
                                dblclick: this.editConta,
                                render: function(g) {
                                    new Ext.LoadMask(
                                        g.getEl(), 
                                        {
                                            store: g.getStore(),
                                            msg: 'Carregando informações do plano de contas'
                                        }
                                    )
                                }
                            },
                            region: 'center',
                            bodyStyle: {
                                borderLeft: 'none',
                                borderRight: 'none',
                                borderBottom: 'none'
                            },
                            store: store,
                            tbar: new Ext.Toolbar({
                                style: 'border-left:none;border-right:none',
                                items: [
                                    {
                                        text: 'Novo',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/images/add.png',
                                        scope: this,
                                        handler: this.addConta
                                    },
                                    {
                                        text: 'Editar',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/images/edit.png',
                                        scope: this,
                                        handler: this.editConta
                                    },
                                    {
                                        text: 'Remover',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/images/delete.png',
                                        scope: this,
                                        handler: this.deleteBatchConta
                                    },
                                    '-',
                                    {
                                        text: 'Transportar',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/rh/images/paste.png',
                                        scope: this,
                                        handler: this.copyContaTipo
                                    },
                                    '-'
                                ]
                            })
                        });
                    }
                    
                    return this.contaPanel;
                },
                
                editPlano: function() {
                    var selected = this.getPlanoPanel().getSelectionModel().getSelected();
            
                    if(selected) {
                        new toolkit.gfp.planoconta.PlanoRestful({
                            method: 'PUT',
                            baseParams: { pk: selected.get('pk') },
                            values: {
                                tipo: selected.get('tipo_value'),
                                folha_tipo: selected.get('folha_tipo__pk'),
                                pessoa_juridica: selected.get('pessoa_juridica__pk'),
                                ano_calendario: selected.get('ano_calendario'),
                                titulo: selected.get('titulo'),
                                banco: selected.get('banco_pk'),
                                agencia: selected.get('agencia'),
                                conta: selected.get('conta'),
                                eventos: selected.get('eventos'),
                            },
                            scope: this,
                            callback: function() {
                                var ac = this.getAnoCalendario().getValue();
                                this.getAnoCalendario().getStore().reload();
                                this.getAnoCalendario().setValue(ac);
                            }
                        }).show()
                    }
                    else alert('Primeiro você deve um item para edição.')
                },
        
                deleteBatchPlano: function() {
                    var selections = this.getPlanoPanel().getSelectionModel().getSelections();
                    var pks = [];
                    
                    if(selections) {
                        Ext.each(
                            selections,
                            function(i) {
                                pks.push(i.get('pk'));
                            }
                        );
                        
                        Ext.Msg.show({
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            title: 'Removendo itens',
                            msg: 'Tem certeza que deseja remover os item(ns) selecionado(s)?',
                            scope: this,
                            fn: function(b) {
                                if(b == 'yes') {
                                    Ext.Ajax.request({
                                        url: toolkit.util.Normalize.controller_action('PCPlano'),
                                        method: 'POST',
                                        params: { pks: pks },
                                        success: function() {
                                            var ac = this.getAnoCalendario().getValue();
                                            this.getAnoCalendario().getStore().reload();
                                            this.getAnoCalendario().setValue(ac);
                                        },
                                        scope: this,
                                        headers: {
                                            'Restful-Method': 'DELETE'
                                        }
                                    });
                                }
                            }
                        });
                    }
                    else alert('Primeiro você deve selecionar os itens para serem removidos.')
                },
                
                addPlano: function() {
                    new toolkit.gfp.planoconta.PlanoRestful({
                        scope: this,
                        callback: function() {
                            var ac = this.getAnoCalendario().getValue();
                            this.getAnoCalendario().getStore().reload();
                            this.getAnoCalendario().setValue(ac);
                        }
                    }).show()
                },
                
                copyPlanoForEmpresa: function() {
                    var grid = this.getPlanoPanel();
                    var selected = grid.getSelectionModel().getSelected();
            
                    if(selected) {
                        new Ext.Window({
                            title: 'Transportar informações de empresa',
                            modal: true,
                            border: false,
                            closable: true,
                            resizable: false,
                            width: 465,
                            buttons: [
                                {
                                    text: 'Transportar',
                                    handler: function(b) {
                                        var wnd = b.ownerCt.ownerCt;
                                        var fp = wnd.getComponent('formPanel');
                                        var form = fp.getForm();
                                        
                                        form.waitMsgTarget = fp.getEl();
                                        form.submit({
                                            url: toolkit.util.Normalize.controller_action('PCGestor', 'copy_plano_empresa'),
                                            params: {
                                                src: selected.get('pk')
                                            },
                                            success: function(action, form) {
                                                grid.getStore().reload();
                                                action.ownerCt.destroy();
                                            },
                                            failure: function(action, form) {
                                                console.debug(action, form)
                                            },
                                            waitMsg: 'Transportando informações...'
                                        });
                                    }
                                },
                                {
                                    text: 'Cancelar',
                                    handler: function(b) { b.ownerCt.ownerCt.destroy() }
                                }
                            ],
                            items: {
                                id: 'formPanel',
                                xtype: 'form',
                                frame: true,
                                width: 450,
                                items: [
                                    {
                                        frame: true,
                                        xtype: 'multiselectbox',
                                        fieldLabel: 'Destinos',
                                        hiddenName: 'dsts',
                                        name: 'dsts',
                                        displayField: 'description',
                                        valueField: 'pk',
                                        controller: 'RHPessoaJuridica',
                                        model: {
                                            'pkg': 'rh',
                                            'name': 'pessoajuridica'
                                        }
                                    }
                                ]
                            }
                        }).show()
                    }
                    else alert('Primeiro você deve um item para ser copiado.')
                },
                
                copyAnoCalendario: function() {
                    var combo = this.getAnoCalendario();
                    var selected = combo.getValue();
            
                    if(selected) {
                        new Ext.Window({
                            title: 'Transportar informações de ano calendario',
                            modal: true,
                            border: false,
                            closable: true,
                            resizable: false,
                            width: 455,
                            buttons: [
                                {
                                    text: 'Transportar',
                                    handler: function(b) {
                                        var wnd = b.ownerCt.ownerCt;
                                        var fp = wnd.getComponent('formPanel');
                                        var form = fp.getForm();
                                        
                                        form.waitMsgTarget = fp.getEl();
                                        form.submit({
                                            url: toolkit.util.Normalize.controller_action('PCGestor', 'copy_ano_calendario'),
                                            params: {
                                                src: selected
                                            },
                                            success: function(form, action) {
                                                combo.getStore().reload();
                                                form.ownerCt.destroy();
                                            },
                                            failure: function(action, form) {
                                                console.debug(action, form)
                                            },
                                            waitMsg: 'Transportando informações...'
                                        });
                                    }
                                },
                                {
                                    text: 'Cancelar',
                                    handler: function(b) { b.ownerCt.ownerCt.destroy() }
                                }
                            ],
                            items: {
                                id: 'formPanel',
                                xtype: 'form',
                                frame: true,
                                width: 450,
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        fieldLabel: 'Destino',
                                        name: 'dst',
                                        width: 320
                                    }
                                ]
                            }
                        }).show()
                    }
                    else alert('Primeiro você deve um item para ser copiado.')
                },
                
                getPlanoPanel: function() {
                    if(!this.planoPanel) {
                        var store = new Ext.data.JsonStore({
                            url: toolkit.util.Normalize.controller_action('PCPlano', 'list_from_year'),
                            fields: [
                                'pk', 'titulo', 'folha_tipo', 'folha_tipo__pk', 
                                'pessoa_juridica', 'pessoa_juridica__pk', 'tipo_value', 
                                'tipo', 'ano_calendario', 'banco_pk', 'agencia', 'conta',
                                'eventos'
                            ],
                            root: 'root',
                            method: 'GET'
                        });
                        
                        this.planoPanel = new Ext.grid.GridPanel({
                            sm: new Ext.grid.RowSelectionModel({
                                listeners: {
                                    scope: this,
                                    rowselect: function(sm, index, record) { this.setPlano(record) }
                                }
                            }),
                            region: 'north',
                            split: true,
                            minHeight: 210,
                            height: 210,
                            bodyStyle: {
                                borderLeft: 'none',
                                borderRight: 'none'
                            },
                            listeners: {
                                scope: this,
                                dblclick: function(g) {
                                    this.editPlano();
                                },
                                render: function(g) {
                                    
                                    new Ext.LoadMask(
                                        g.getEl(),
                                        {
                                            store: g.getStore(),
                                            msg: 'Carregando os planos de contas para o ano calendário selecionado.'
                                        }
                                    )
                                    
                                }
                            },
                            store: store,
                            autoExpandColumn: 'autoExpand',
                            cm: new Ext.grid.ColumnModel([
                                {
                                    id: 'status',
                                    header: 'Tipo',
                                    dataIndex: 'tipo',
                                    width: 160,
                                    menuDisabled: true,
                                    renderer: toolkit.util.formatStatusLabel
                                },
                                {
                                    header: 'Folha',
                                    dataIndex: 'folha_tipo',
                                    sortable: true,
                                    width: 160
                                },
                                {
                                    id: 'autoExpand',
                                    header: 'Título',
                                    dataIndex: 'titulo'
                                },
                                {
                                    header: 'Pessoa Juridica',
                                    dataIndex: 'pessoa_juridica',
                                    width: 250
                                },
                            ]),
                            tbar: new Ext.Toolbar({
                                style: 'border-left:none;border-top:none;border-right:none',
                                items: [
                                    {
                                        text: 'Novo',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/images/add.png',
                                        scope: this,
                                        handler: this.addPlano
                                    },
                                    {
                                        text: 'Editar',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/images/edit.png',
                                        scope: this,
                                        handler: this.editPlano
                                    },
                                    {
                                        text: 'Remover',
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/images/delete.png',
                                        scope: this,
                                        handler: this.deleteBatchPlano
                                    },
                                    '-',
                                    {
                                        iconCls: true,
                                        icon: '/' + global.Context + '/static/rh/images/paste.png',
                                        text: 'Transportar',
//                                         split: true,
//                                         defaultType: 'splitbutton',
                                        menu: [
                                            {
                                                text: 'de empresa',
                                                scope: this,
                                                handler: this.copyPlanoForEmpresa
                                            },
                                            {
                                                text: 'de ano calendário',
                                                scope: this,
                                                handler: this.copyAnoCalendario
                                            }
                                        ]
                                    },
                                    '-',
                                    '->',
                                    '-',
                                    ' ',
                                    {
                                        xtype: 'combo',
                                        emptyText: 'Filtrar por tipo',
                                        width: 150,
                                        triggerAction: 'all',
                                        editable: false,
                                        store: [
                                            [0, 'TODOS'],
                                            [1, 'CONSIGNAÇÃO'],
                                            [2, 'LIQUIDO'],
                                            [3, 'PATRONAL'],
                                            // [4, 'SALARIO FAMILIA'],
                                            // [5, 'AUXILIO TRANSPORTE'],
                                            // [6, 'PENSÃO ALIMENTICIA'],
                                            // [7, 'AUXÍLIO CRECHE'],
                                            // [8, 'DEP. JUDICIAL'],
                                        ],
                                        listeners: {
                                            scope: this,
                                            select: function(combo, record, index) {
                                                var store = this.getPlanoPanel().getStore();
                                                
                                                if(record.get('field1') == 0) 
                                                    delete store.baseParams['f__tipo'];
                                                else store.baseParams['f__tipo'] = record.get('field1');
                                                
                                                store.load({});
                                            }
                                        }
                                    },
                                    ' ',
                                    '-',
                                    ' ',
                                    {
                                        xtype: 'combo',
                                        emptyText: 'Filtrar por folha',
                                        width: 180,
                                        store: new Ext.data.JsonStore({
                                            fields: ['pk', 'description'],
                                            root: 'root',
                                            proxy: new Ext.data.HttpProxy({
                                                url: toolkit.util.Normalize.controller_action('PCGestor', 'list_folha_tipo'),
                                                method: 'GET'
                                            }),
                                            autoLoad: true
                                        }),
                                        
                                        displayField: 'description',
                                        valueField: 'pk',
                                        triggerAction: 'all',
                                        editable: false,
                                        listeners: {
                                            scope: this,
                                            select: function(combo, record, index) {
                                                var store = this.getPlanoPanel().getStore();
                                                
                                                if(record.get('pk') == 0) 
                                                    delete store.baseParams['f__folha_tipo'];
                                                else store.baseParams['f__folha_tipo'] = record.get('pk');
                                                
                                                store.load({});
                                            }
                                        }
                                    },
                                    ' ',
                                    '-',
                                    ' ',
                                    this.getAnoCalendario(),
                                    ' '
                                ]
                            })
                        })
                    }
                    
                    return this.planoPanel;
                },
                
                getAnoCalendario: function() {
                    if(!this.anoCalendario) {
                        var sto = new Ext.data.JsonStore({
                            url: toolkit.util.Normalize.controller_action('PCGestor', 'list_ano_calendario'),
                            fields: ['ano', 'description'],
                            autoLoad: true,
                            root: 'result',
                            listeners: {
                                scope: this,
                                load: function(store) {
                                    if(store.getCount()) {
                                        this.getAnoCalendario().setValue(store.getAt(0).get('ano'));
                                        this.setAnoCalendario(store.getAt(0).get('ano'));
                                    }
                                }
                            }
                        });
                        
                        this.anoCalendario = new Ext.form.ComboBox({
                            store: sto,
                            displayField: 'description',
                            valueField: 'ano',
                            editable: false,
                            emptyText: 'Ano Calendário',
                            triggerAction: 'all',
                            mode: 'local',
                            width: 150,
                            listeners: {
                                scope: this,
                                select: function(combo, record) {
                                    this.setAnoCalendario(record.get('ano'));
                                }
                            }
                        });
                    }
                    
                    return this.anoCalendario;
                },
                
                setAnoCalendario: function(ano_calendario) {
                    var store = this.getPlanoPanel().getStore();
                    
                    store.baseParams.ano_calendario = ano_calendario
                    store.load({});
                },
                
                constructor: function() {
                    var cf = {
                        title: 'Gestor de Planos de Contas',
                        closable: true,
                        layout: 'border',
                        border: false,
                        items: [
                            this.getPlanoPanel(),
                            this.getContaPanel()
                        ]
                    };
                    
                    toolkit.gfp.planoconta.Gestor.superclass.constructor.call(this, cf);

                    var ts = toolkit.Application.tabspace;

                    ts.remove(ts.getActiveTab());
                    ts.add(this);
                    ts.setActiveTab(this);
                }
            }
        )
    }
);