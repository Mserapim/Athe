/**
 * 
 * 
 */

Ext.ns('toolkit.gfp.dirf');

toolkit.gfp.dirf.IRRFFaixaRestForm = Ext.extend(
    toolkit.restful.FormPanel,
    {
        router: toolkit.util.Normalize.controller_action('DIRFIRRFFaixa'),
        
        getFormPanel: function() {
            if(!this.formPanel) {
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    defaults: {
                        width: 350
                    },
                    items: [
                        {
                            "allowBlank": false, 
                            "fieldLabel": "Limite Inferior", 
                            "xtype": "numberfield", 
                            "allowDecimals": true, 
                            "maxLength": 19, 
                            "decimalPrecision": 2, 
                            "value": (this.values.limite_inferior ? this.values.limite_inferior : ''), 
                            "name": "limite_inferior"
                        }, 
                        {
                            "allowBlank": false, 
                            "fieldLabel": "Limite Superior", 
                            "xtype": "numberfield",
                            "allowDecimals": true, 
                            "maxLength": 19,
                            "decimalPrecision": 2,
                            "value": (this.values.limite_superior ? this.values.limite_superior : ''), 
                            "name": "limite_superior"
                        }, 
                        {
                            "allowBlank": false, 
                            "fieldLabel": "Aliquota",
                            "xtype": "numberfield",
                            "allowDecimals": true, 
                            "maxLength": 10,
                            "decimalPrecision": 3, 
                            "value": (this.values.percentual ? this.values.percentual : ''), 
                            "name": "percentual"
                        },
                        {
                            "allowBlank": false, 
                            "fieldLabel": "Dedu\u00e7\u00e3o", 
                            "xtype": "numberfield", 
                            "allowDecimals": true, 
                            "maxLength": 19, 
                            "decimalPrecision": 2, 
                            "value": (this.values.desconto ? this.values.desconto : ''), 
                            "name": "desconto"
                        }
                    ]
                });
            }
            
            return this.formPanel;
        },
        
        constructor: function(cf) {
            if(!cf) cf = {};
            
            var df = {
                modal: true,
                title: 'Nova faixa',
                width: 500,
                border: false
            };
            
            Ext.applyIf(cf, df);
            
            toolkit.gfp.dirf.IRRFFaixaRestForm.superclass.constructor.call(this, cf);
        }
    }
);

toolkit.gfp.dirf.IRRFRestForm = Ext.extend(
    toolkit.restful.FormPanel,
    {
        router: toolkit.util.Normalize.controller_action('DIRFIRRF'),
                                           
        getFormPanel: function() {
            if(!this.formPanel) {
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    defaults: {
                        width: 350
                    },
                    items: [
                        {
                            'displayField': 'description', 
                            'fieldLabel': 'Publica\u00e7\u00e3o', 
                            'allowBlank': false, 
                            'hiddenName': 'publicacao', 
                            'valueField': 'pk', 
                            'conf': {
                                'addLabel': 'Criar ...', 
                                'editLabel': 'Modificar ...', 
                                'canAdd': true, 
                                'canEdit': true
                            }, 
                            'triggerAction': 'all', 
                            'queryAction': 'query', 
                            'model': 'Publicacao', 
                            'hideTrigger': true, 
                            'queryParam': 'keyword', 
                            'crudController': 'RHPublicacao', 
                            'xtype': 'autocompletefield',
                            'value': (this.values.publicacao ? this.values.publicacao : 0)
                        }, 
                        {
                            'allowBlank': false, 
                            'fieldLabel': 'Valor dependente', 
                            'xtype': 'numberfield', 
                            'allowDecimals': true, 
                            'maxLength': 19, 
                            'decimalPrecision': 2, 
                            'name': 'valor_dependente',
                            'value': (this.values.valor_dependente ? this.values.valor_dependente : 0)
                        }, 
                        {
                            'allowBlank': false, 
                            'fieldLabel': 'Ano Calend\u00e1rio', 
                            'xtype': 'numberfield', 
                            'allowDecimals': false, 
                            'name': 'ano_calendario',
                            'value': (this.values.ano_calendario ? this.values.ano_calendario : '')  
                        },{
                            'allowBlank': false,
                            'fieldLabel': 'Data Vigência',
                            'xtype': 'datefield',
                            'name': 'data_vigencia',
                            'value': (this.values.data_vigencia ? this.values.data_vigencia : '')
                        }
                    ]
                })
            }
            
            return this.formPanel;
        },
        
        constructor: function(cf) {
            if(!cf) cf = {};
            
            var df = {
                modal: true,
                title: 'Novo ano base',
                width: 500,
                border: false
            };
            
            Ext.applyIf(cf, df);
            
            toolkit.gfp.dirf.IRRFRestForm.superclass.constructor.call(this, cf);
        }
    }
);

toolkit.gfp.dirf.Configurador = Ext.extend(
    Ext.Panel,
    {
        setAnoBase: function(anobase) {
            this.anoBase = anobase;
            this.getGridFaixa().getStore().baseParams.irrf = this.anoBase;
            this.getGridFaixa().getStore().load({});
        },
        
        addAnoBase: function() {
            new toolkit.gfp.dirf.IRRFRestForm({
                method: 'POST',
                scope: this,
                callback: function(action) {
                    this.getGridAnoBase().getStore().load({});
                }
            }).show();
        },
        
        editAnoBase: function() {
            var selected = this.getGridAnoBase().getSelectionModel().getSelected();
            
            if(selected) {
                new toolkit.gfp.dirf.IRRFRestForm({
                    baseParams: { pk: selected.get('pk') },
                    values: {
                        valor_dependente: selected.get('valor_dependente'),
                        ano_calendario: selected.get('ano_calendario'),
                        publicacao: selected.get('publicacao__pk'),
                        data_vigencia: selected.get('data_vigencia'),
                    },
                    method: 'PUT',
                    scope: this,
                    callback: function(action) {
                        this.getGridAnoBase().getStore().load({});
                    }
                }).show();
            }
            else alert('Primeiro você deve selecionar um ano base.')
        },
        
        deleteBatchAnoBase: function() {
            var selections = this.getGridAnoBase().getSelectionModel().getSelections();
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
                                url: new toolkit.gfp.dirf.IRRFRestForm().router,
                                method: 'POST',
                                params: { pks: pks },
                                success: function() { this.getGridAnoBase().getStore().reload(); },
                                scope: this,
                                headers: {
                                    'Restful-Method': 'DELETE'
                                }
                            });
                        }
                    }
                });
            }
            else alert('Primeiro você deve selecionar um ano calendário.')
        },
        
        copyAnoBase: function() {
            console.info('nao foi implementado')
        },
         
        getGridAnoBase: function() {
            if(!this.gridAnoBase) {
                var store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('GFPIRRF', 'query'),
                    fields: ['pk', 'description', 'valor_dependente', 'ano_calendario', 'publicacao__pk', 'data_vigencia'],
                    root: 'result'
                });
                
                this.gridAnoBase = new Ext.grid.GridPanel({
                    region: 'center',
                    minHeight: 200,
                    store: store,
                    autoExpandColumn: 'description',
                    cm: new Ext.grid.ColumnModel([
                        {
                            header: 'Chave',
                            dataIndex: 'pk',
                            width: 50
                        },
                        {
                            id: 'description',
                            header: 'Descricao',
                            dataIndex: 'description'
                        },
                        {
                            header: 'Dependente',
                            dataIndex: 'valor_dependente',
                            renderer: toolkit.util.formatCurrency,
                            width: 80
                        },
                        {
                            header: 'Data vigência',
                            dataIndex: 'data_vigencia',
//                            renderer: toolkit.util.formatCurrency,
                            width: 80
                        }
                    ]),
                    bbar: new Ext.PagingToolbar({
                        store: store,
                        displayInfo: true,
                        pageSize: 50
                    }),
                    sm: new Ext.grid.RowSelectionModel({
                        listeners: {
                            scope: this,
                            rowselect: function(grid, index, record) {
                                this.setAnoBase(record.get('pk'));
                            }
                        }
                    }),
                    tbar: [
                        {
                            text: 'Novo',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/add.png',
                            scope: this,
                            handler: this.addAnoBase
                        },
                        {
                            text: 'Editar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/edit.png',
                            scope: this,
                            handler: this.editAnoBase
                        },
                        {
                            text: 'Remover',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/delete.png',
                            scope: this,
                            handler: this.deleteBatchAnoBase
                        },
                        '-',
                        {
                            text: 'Copiar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/add.png',
                            scope: this,
                            handler: this.copyAnoBase
                        },
                        '-'
                    ],
                    listeners: {
                        render: function(p) {
                            new Ext.LoadMask(
                                p.getEl(),
                                {
                                    store: p.getStore(),
                                    msg: 'Carregando a configurações do Imposto de Renda'
                                }
                            );
                            
                            p.getStore().load({});
                        }
                    }
                });
            }
            
            return this.gridAnoBase;
        },
        
        addFaixa: function() {
            new toolkit.gfp.dirf.IRRFFaixaRestForm({
                method: 'POST',
                scope: this,
                callback: function(action) {
                    this.getGridFaixa().getStore().load({});
                },
                baseParams: {
                    irrf: this.anoBase
                }
            }).show();
        },
        
        editFaixa: function() {
            var selected = this.getGridFaixa().getSelectionModel().getSelected();
            
            if(selected) {
                new toolkit.gfp.dirf.IRRFFaixaRestForm({
                    baseParams: { pk: selected.get('pk') },
                    values: {
                        limite_inferior: selected.get('limite_inferior'),
                        limite_superior: selected.get('limite_superior'),
                        desconto: selected.get('desconto'),
                        percentual: selected.get('percentual')
                    },
                    method: 'PUT',
                    scope: this,
                    callback: function(action) {
                        this.getGridFaixa().getStore().load({});
                    }
                }).show();
            }
            else alert('Primeiro você deve selecionar um ano base.')
        },
        
        deleteBatchFaixa: function() {
            var selections = this.getGridFaixa().getSelectionModel().getSelections();
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
                                url: new toolkit.gfp.dirf.IRRFFaixaRestForm().router,
                                method: 'POST',
                                params: { pks: pks },
                                success: function() { this.getGridFaixa().getStore().reload(); },
                                scope: this,
                                headers: {
                                    'Restful-Method': 'DELETE'
                                }
                            });
                        }
                    }
                });
            }
            else alert('Primeiro você deve selecionar uma faixa.')
        },
        
        getGridFaixa: function() {
            if(!this.gridFaixa) {
                var store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('DIRFConfigurador', 'faixa_ano_base'),
                    fields: ['pk', 'limite_inferior', 'limite_superior', 'percentual', 'desconto'],
                    root: 'result'
                });
                
                this.gridFaixa = new Ext.grid.GridPanel({
                    region: 'south',
                    minHeight: 200,
                    height: 300,
                    split: true,
                    cm: new Ext.grid.ColumnModel([
                        {
                            header: 'Chave',
                            dataIndex: 'pk'
                        },
                        {
                            header: 'Limite Inferior',
                            dataIndex: 'limite_inferior',
                            renderer: toolkit.util.formatCurrency
                        },
                        {
                            header: 'Limite Superior',
                            dataIndex: 'limite_superior',
                            renderer: toolkit.util.formatCurrency
                        },
                        {
                            header: 'Aliquota',
                            dataIndex: 'percentual',
                            renderer: toolkit.util.formatCurrency
                        },
                        {
                            header: 'Dedução',
                            dataIndex: 'desconto',
                            renderer: toolkit.util.formatCurrency
                        }
                    ]),
                    store: store,
                    bbar: new Ext.PagingToolbar({
                        store: store,
                        displayInfo: true,
                        pageSize: 50
                    }),
                    tbar: [
                        {
                            text: 'Novo',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/add.png',
                            scope: this,
                            handler: this.addFaixa
                        },
                        {
                            text: 'Editar',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/edit.png',
                            scope: this,
                            handler: this.editFaixa
                        },
                        {
                            text: 'Remover',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/delete.png',
                            scope: this,
                            handler: this.deleteBatchFaixa
                        },
                        '-'
                    ],
                    listeners: {
                        render: function(p) {
                            new Ext.LoadMask(
                                p.getEl(),
                                {
                                    store: p.getStore(),
                                    msg: 'Carregando as faixas do Imposto de Renda'
                                }
                            );
                        }
                    }
                });
            }
            
            return this.gridFaixa;
        },
        
        constructor: function() {
            var cf = {
                title: 'Configurador do Imposto de Renda',
                closable: true,
                layout: 'border',
                border: false,
                items: [
                    this.getGridAnoBase(),
                    this.getGridFaixa()
                ]
            };
            
            toolkit.gfp.dirf.Configurador.superclass.constructor.call(this, cf);

            var ts = toolkit.Application.tabspace;

            ts.remove(ts.getActiveTab());
            ts.add(this);
            ts.setActiveTab(this);
        }
    }
)

toolkit.gfp.dirf.Gerador = Ext.extend(
    Ext.form.FormPanel,
    {
        getProgressBar: function() {
            if(!this.pbar) {
                this.pbar = new Ext.ProgressBar(
                    {
                        labelSeparator: ' ...',
                        fieldLabel: 'Aguardando andamento geral',
                        xtype: 'progress',
                        border: false,
                        submit: false
                    }
                );
            }

            return this.pbar;
        },

        getAnoBaseCombo: function() {
            if(!this.anobaseCombo) {
                this.anobaseCombo = new Ext.form.ComboBox({
                    xtype: 'combo',
                    hiddenName: 'ano',
                    displayField: 'description',
                    valueField: 'anobase',
                    store: new Ext.data.JsonStore({
                        proxy: new Ext.data.HttpProxy({
                            url: toolkit.util.Normalize.controller_action('DIRFDialect', 'listDirf'),
                            method: 'GET',
                            disableCaching: false
                        }),
                        fields: ['anobase', 'description', 'dialect'],
                        root: 'root'
                    }),
                    triggerAction: 'all',
                    fieldLabel: 'DIRF para database'
                });
            }

            return this.anobaseCombo
        },
        
        constructor: function() {
            var cf = {
                width: 555,
                frame: true,
                border: false,
                defaults: {
                    width: 415
                },
                labelWidth: 110,
                labelAlign: 'right',
                items: [
                    this.getAnoBaseCombo(),
                    {
                        xtype: 'checkbox',
                        fieldLabel: 'Retificadora',
                        name: 'retificadora'
                    },
                    {
                        xtype: 'checkbox',
                        fieldLabel: 'Públicar',
                        name: 'publicar'
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Ultimo Recibo',
                        name: 'recibo_numero'
                    },
                    {
                        fieldLabel: 'Status',
                        xtype: 'panel',
                        layout: 'form',
                        labelAlign: 'top',
                        frame: true,
                        items: [this.getProgressBar()]
                    },
                ],
                buttons: [
                    {
                        text: 'Gerar DIRF',
                        handler: this.start,
                        scope: this
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: function() { this.ownerCt.destroy() }
                    }
                ]
            };

            toolkit.gfp.dirf.Gerador.superclass.constructor.call(this, cf);
        },

        start: function() {
            var values = this.getForm().getValues();

            if(values.retificadora && values.recibo_numero == '')
                alert('Para declarações retificadora é necessário um número de recibo.')
            else {

                var store = this.getAnoBaseCombo().getStore();
                var rec = store.getAt(store.find('anobase', values.ano));

                var p = {}
                p.anobase = values.ano;
                p.dialect = rec.get('dialect');

                if(values.retificadora) {
                    p.retificadora = true,
                    p.recibo = values.recibo_numero
                }

                if(values.publicar == 'on') p.publicar = true;
                
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        'DIRFDialect',
                        'createSessionId'
                    ),
                    params: p,
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        this.processSession(obj)
                    },
                    failure: function(request) {
                        alert('Ocorreu um erro, tente novamente mais tarde.')
                    },
                    scope: this
                })
            }
        },

        processSession: function(obj) {
            this.task = Ext.TaskMgr.start({
                interval: (10 * 1000),
                run: this.updateProgress,
                scope: this,
                args: [obj.sid]
            });

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'DIRFDialect',
                    'start'
                ),
                params: {
                    sid: obj.sid
                },
                scope: this
            });
        },

        updateProgress: function(sid) {
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'DIRFDialect',
                    'getSessionInformation'
                ),
                params: {
                    sid: sid
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);

                    if(obj.done && !obj.error) {
                        var url = toolkit.util.Normalize.controller_action(
                            'DIRFDialect',
                            'getFile'
                        ) + '?sid=' + obj.sid + '&anobase=' + obj.anobase;
                        
                        var width  = 235;
                        var height = 175;
                        var left   = (screen.width - width) / 2;
                        var top    = (screen.height - height) / 2;
                        
                        window.open(url, "_self");
                        
                        Ext.TaskMgr.stop(this.task);
                        
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'DIRFDialect',
                                'destroySession'
                            ),
                            params: { sid: obj.sid }
                        });
                    }
                    else if(obj.error) {
                        
                        Ext.TaskMgr.stop(this.task);
                        alert(obj.error);

                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'DIRFDialect',
                                'destroySession'
                            ),
                            params: { sid: obj.sid }
                        });
                        
                    }
                    
                    if(obj.pct) this.getProgressBar().updateProgress(obj.pct, obj.pctText, true);
                    else this.getProgressBar().updateProgress(0, 'Aguardando informações', true);
                },
                scope: this
            });
        }
    }
)

toolkit.gfp.dirf.TokenRestForm = Ext.extend(
    toolkit.restful.FormPanel,
    {
        router: toolkit.util.Normalize.controller_action('DIRFToken'),
                                              
        constructor: function(cf) {
            
            if(!cf) cf = {};
            
            var df = {
                modal: true,
                title: 'Criar informações para o formato',
                width: 500,
                border: false
            };
            
            Ext.applyIf(cf, df);
            
            toolkit.gfp.dirf.TokenRestForm.superclass.constructor.call(this, cf);
        },
        
        getFormPanel: function() {
            if(!this.formPanel) {
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    defaults: {
                        width: 365
                    },
                    items: [
                        {
                            xtype: 'textfield',
                            name: 'nome',
                            fieldLabel: 'Nome do campo',
                            value: this.values.nome
                        },
                        {
                            xtype: 'textfield',
                            name: 'id_receita',
                            fieldLabel: 'Código da Receita',
                            value: this.values.id_receita
                        },
                        {
                            xtype: 'combo',
                            hiddenName: 'tipo',
                            fieldLabel: 'Tipo do campo',
                            store: [
                                [1, 'RENDIMENTO'],
                                [2, 'DESPESA']
                            ],
                            value: this.values.tipo
                        },
                        {
                            name: 'eventos',
                            fieldLabel: 'Eventos',
                            xtype: 'multiselectbox',
                            controller: 'GFPEvento',
                            model: {
                                name: 'Evento',
                                pkg: 'rh.gfp.models'
                            },
                            value: this.values.eventos
                        }
                    ]
                });
            }
            
            return this.formPanel;
        }
    }
);

toolkit.gfp.dirf.DialectRestForm = Ext.extend(
    toolkit.restful.FormPanel,
    {
        router: toolkit.util.Normalize.controller_action('DIRFDialect'),
                                              
        constructor: function(cf) {
            
            if(!cf) cf = {};
            
            var df = {
                modal: true,
                title: 'Criar um novo formato de arquivo da Receita Federal do Brasil',
                width: 400,
                border: false
            };
            
            Ext.applyIf(cf, df);
            
            toolkit.gfp.dirf.DialectRestForm.superclass.constructor.call(this, cf);
        },
        
        getFormPanel: function() {
            if(!this.formPanel) {
                var storeDirf = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('GFPIRRF', 'query'),
                    fields: ['pk', 'description'],
                    root: 'result',
                    listeners: {
                        scope: this,
                        load: function() {
                            this.getFormPanel().getForm().findField('dirf').setValue(this.values.dirf);
                        }
                    }
                });
                
                var storeEngine = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('DIRFDialect', 'engineList'),
                    fields: ['key', 'description'],
                    root: 'root',
                    listeners: {
                        scope: this,
                        load: function() {
                            this.getFormPanel().getForm().findField('engine').setValue(this.values.engine);
                        }
                    }
                });
                
                storeDirf.load({});
                storeEngine.load({});
                
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    defaults: {
                        width: 265
                    },
                    items: [
                        {
                            fieldLabel: 'Para',
                            xtype: 'combo',
                            store: storeDirf,
                            displayField: 'description',
                            valueField: 'pk',
                            hiddenName: 'dirf',
                            triggerAction: 'all',
                            mode: 'local',
                            emptyText: 'Selecione um item'
                        },{
                            fieldLabel: 'Formato',
                            xtype: 'combo',
                            store: storeEngine,
                            displayField: 'description',
                            valueField: 'key',
                            hiddenName: 'engine',
                            triggerAction: 'all',
                            mode: 'local',
                            emptyText: 'Selecione um item'
                        },{
                            displayField: "description", 
                            fieldLabel: "Cópia de", 
                            allowBlank: true, 
                            hiddenName: "copy_from", 
                            valueField: "pk", 
                            conf: {
                                canAdd: false, 
                                canEdit: false
                            }, 
                            triggerAction: "all", 
                            genericCrud: true, 
                            queryAction: "query", 
                            model: {
                                name: "dialect", 
                                app_label: "dirf"
                            }, 
                            hideTrigger: true, 
                            queryParam: "keyword", 
                            xtype: "autocompletefield"
                        },{
                            xtype: 'textfield',
                            name: 'identificador_layout',
                            fieldLabel: 'Identificador',
                            value: this.values.identificador_layout                            
                        } 
                    ]
                });
            }
                
            return this.formPanel;
        }
    }
)

toolkit.gfp.dirf.DialectController = Ext.extend(
    Ext.Panel,
    {
        newDialect: function() {
            new toolkit.gfp.dirf.DialectRestForm({
                method: 'POST',
                scope: this,
                callback: function(action) {
                    this.getDialectGrid().getStore().load({});
                }
            }).show();
        },
        
        editDialect: function() {
            var selected = this.getDialectGrid().getSelectionModel().getSelected();
            
            if(selected) {
                console.debug(selected);
                new toolkit.gfp.dirf.DialectRestForm({
                    baseParams: { pk: selected.get('pk') },
                    values: {
                        description: selected.get('description'),
                        dirf: selected.get('dirf'),
                        engine: selected.get('engine'),
                        copy_from: selected.get('copy_from'),
                        identificador_layout: selected.get('identificador_layout')
                    },
                    method: 'PUT',
                    scope: this,
                    callback: function(action) {
                        this.getDialectGrid().getStore().load({});
                    }
                }).show();
            }
            else alert('Primeiro você deve selecionar um formato de arquivo.')
        },
        
        deleteDialects: function() {
            var selections = this.getDialectGrid().getSelectionModel().getSelections();
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
                                url: toolkit.util.Normalize.controller_action('DIRFDialect'),
                                method: 'POST',
                                params: { pks: pks },
                                success: function() { this.getDialectGrid().getStore().reload(); },
                                scope: this,
                                headers: {
                                    'Restful-Method': 'DELETE'
                                }
                            });
                        }
                    }
                });
            }
            else alert('Primeiro você deve selecionar um ou mais formatos de arquivo.')
        },
        
        getDialectGrid: function() {
            if(!this.dialectGrid) {
                var store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('DIRFDialect'),
                    fields: ['pk','description','dirf', 'engine', 'copy_from', 'identificador_layout'],
                    totalProperty: 'totalRows',
                    root: 'root',
                    restful: true
                });
                
                this.dialectGrid = new Ext.grid.GridPanel({
                    region: 'center',
                    tbar: [
                        {
                            text: 'Novo',
                            handler: this.newDialect,
                            scope: this,
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/add.png"
                        },
                        {
                            text: 'Editar',
                            handler: this.editDialect,
                            scope: this,
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/edit.png"
                        },
                        {
                            text: 'Remover',
                            handler: this.deleteDialects,
                            scope: this,
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/delete.png"
                        },
                        '-'
                    ],
                    autoExpandColumn: 'descriptionColumn',
                    cm: new Ext.grid.ColumnModel([
                        {dataIndex: 'pk', header: 'Chave', sortable: true, width: 90},
                        {dataIndex: 'description', header: 'Descrição', sortable: true, id: 'descriptionColumn'}
                    ]),
                    sm: new Ext.grid.RowSelectionModel({
                        listeners: {
                            scope: this,
                            rowselect: function(sm, rowIndex, record) {
                                this.getTokenGrid().dialect = record.get('pk');
                                this.getTokenGrid().getStore().baseParams['dialect'] = record.get('pk');
                                this.getTokenGrid().getStore().load({});
                            }
                        }
                    }),
                    bbar: new Ext.PagingToolbar({
                        store: store,
                        displayInfo: true,
                        pageSize: 50
                    }),
                    store: store,
                    listeners: {
                        render: function(g) {
                            new Ext.LoadMask(
                                g.getEl(), 
                                {
                                    msg: 'Buscando informações no servidor.', 
                                    store: g.getStore()
                                }
                            );
                            g.getStore().load({});
                        },
                        dblclick: this.editDialect,
                        keypress: function(e) {
                            if(e.getKey() == e.ENTER)
                                this.editDialect()
                            else if(e.getKey() == e.DELETE)
                                this.deleteDialects()
                            else if(e.getKey() == e.INSERT)
                                this.newDialect()
                        },
                        scope: this
                    }
                });
            }
            
            return this.dialectGrid;
        },
        
        newToken: function() {
            new toolkit.gfp.dirf.TokenRestForm({
                baseParams: {
                    dialect: this.getTokenGrid().dialect
                },
                method: 'POST',
                scope: this,
                callback: function(action) {
                    this.getTokenGrid().getStore().reload();
                }
            }).show();
        },

        editToken: function() {
            var selected = this.getTokenGrid().getSelectionModel().getSelected();

            if(selected) {
                new toolkit.gfp.dirf.TokenRestForm({
                    baseParams: {
                        pk: selected.get('pk'),
                        dialect: selected.get('dialect')
                    },
                    values: {
                        nome: selected.get('description'),
                        eventos: selected.get('eventos'),
                        id_receita: selected.get('id_receita'),
                        tipo: selected.get('tipo')
                                        
                    },
                    method: 'PUT',
                    scope: this,
                    callback: function(action) {
                        this.getTokenGrid().getStore().load({});
                    }
                }).show();
            }
            else alert('Primeiro você deve selecionar um formato de arquivo.')
        },

        deleteToken: function() {
            var selections = this.getTokenGrid().getSelectionModel().getSelections();
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
                                url: toolkit.util.Normalize.controller_action('DIRFToken'),
                                method: 'POST',
                                params: { pks: pks },
                                success: function() { this.getTokenGrid().getStore().reload(); },
                                scope: this,
                                headers: {
                                    'Restful-Method': 'DELETE'
                                }
                            });
                        }
                    }
                });
            }
            else alert('Primeiro você deve selecionar um ou mais formatos de arquivo.')
        },
        
        getTokenGrid: function() {
            if(!this.tokenGrid) {
                var store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('DIRFToken'),
                    fields: ['pk','description', 'eventos', 'dialect', 'id_receita', 'tipo'],
                    totalProperty: 'totalRows',
                    root: 'root',
                    restful: true
                });
                
                this.tokenGrid = new Ext.grid.GridPanel({
                    region: 'south',
                    height: 280,
                    minHeight: 280,
                    maxHeight: 280,
                    split: true,
                    tbar: [
                        {
                            text: 'Novo',
                            scope: this,
                            handler: this.newToken,
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/add.png"
                        },
                        {
                            text: 'Editar',
                            iconCls: true,
                            scope: this,
                            handler: this.editToken,
                            icon: "/" + global.Context + "/static/images/edit.png"
                        },
                        {
                            text: 'Remover',
                            iconCls: true,
                            scope: this,
                            handler: this.deleteToken,
                            icon: "/" + global.Context + "/static/images/delete.png"
                        },
                        '-'
                    ],
                    autoExpandColumn: 'descriptionColumn',
                    cm: new Ext.grid.ColumnModel([
                        {dataIndex: 'pk', header: 'Chave', sortable: true, width: 90},
                        {dataIndex: 'description', header: 'Descrição', sortable: true, id: 'descriptionColumn'}
                    ]),
                    bbar: new Ext.PagingToolbar({
                        store: store,
                        displayInfo: true,
                        pageSize: 50
                    }),
                    store: store,
                    listeners: {
                        render: function(g) {
                            new Ext.LoadMask(
                                g.getEl(), 
                                {
                                    msg: 'Buscando informações no servidor.', 
                                    store: store
                                }
                            );
                        },
                        dblclick: this.editToken,
                        keypress: function(e) {
                            if(e.getKey() == e.ENTER)
                                this.editToken()
                            else if(e.getKey() == e.DELETE)
                                this.deleteToken()
                            else if(e.getKey() == e.INSERT)
                                this.newToken()
                        },
                        scope: this
                    }
                });
            }
            
            return this.tokenGrid;
        },
        
        constructor: function() {
            
            var cf = {
                title: 'Formato do Arquivo RFB',
                closable: true,
                layout: 'border',
                border: false,
                items: [
                    this.getDialectGrid(),
                    this.getTokenGrid()
                ]
            };
            
            toolkit.gfp.dirf.DialectController.superclass.constructor.call(this, cf);

            var ts = toolkit.Application.tabspace;

            ts.remove(ts.getActiveTab());
            ts.add(this);
            ts.setActiveTab(this);
            
        }
        
    }
);