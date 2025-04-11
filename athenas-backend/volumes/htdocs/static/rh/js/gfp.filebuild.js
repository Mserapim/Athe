
Ext.ns('toolkit.gfp');

Ext.apply(
    toolkit.gfp,
    {
        CSVContaCredito: Ext.extend(
            toolkit.widget.CommanderController,
            {
                getFormPanel: function() {
                    if(!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            border: false,
                            defaults: {
                                width: 280
                            },
                            items: [
                                // {
                                //     hiddenName: 'tipo_folha',
                                //     xtype: 'combo',
                                //     fieldLabel: 'Tipo da Folha',
                                //     store: new Ext.data.JsonStore({
                                //         url: toolkit.util.Normalize.controller_action('GFPFolhaTipo', 'query'),
                                //         autoLoad: true,
                                //         root: 'result',
                                //         fields: ['pk', 'description']
                                //     }),
                                //     mode: 'local',
                                //     triggerAction: 'all',
                                //     displayField: 'description',
                                //     valueField: 'pk'
                                // },
                                 {
                                    xtype: "rest-autocompletefield", 
                                    fieldLabel: "Tipo da Folha", 
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.PayrollTypeRestful", 
                                    name: "tipo_folha"
                                }, 
                                {
                                    hiddenName: 'tipo_servidor',
                                    xtype: 'combo',
                                    fieldLabel: 'Tipo de Servidor',
                                    store: [
                                        [1, 'TODOS'],
//                                         [2, 'EFETIVOS'],
//                                         [3, 'COMISSIONADOS'],
//                                         [4, 'EXCLUSIVAMENTE COMISSIONADOS'],
//                                         [5, 'MEMBROS'],
                                    ],
                                    triggerAction: 'all',
                                    value: 1
                                },
                                {
                                    hiddenName: 'situacao_servidor',
                                    xtype: 'combo',
                                    fieldLabel: 'Situação',
                                    store: [
                                        [1, 'TODOS'],
                                        [2, 'ATIVO'],
                                        [3, 'INATIVO']
                                    ],
                                    triggerAction: 'all',
                                    value: 2
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'Progresso da Geração',
                                    width: 385,
                                    items: this.getProgressBar()
                                }
                            ]
                        });
                    
                    return this.formPanel;
                },
                
                getProgressBar: function() {
                    if(!this.progressBar)
                        this.progressBar = new Ext.ProgressBar();
                    
                    return this.progressBar;
                },
                
                update: function(obj) {
                    this.getProgressBar().updateProgress(obj.pct, obj.pctText, true)
                },
                
                controller: 'GFPContaCreditoCSV',
                
                constructor: function() {
                    var cf = {
                        title: 'Extrator de Contas de Crédito dos Servidores',
                        width: 415,
                        border: false,
                        closable: true,
                        items: this.getFormPanel(),
                        modal: true,
                        buttons: [
                            {
                                text: 'Gerar',
                                scope: this,
                                handler: this.start
                            },
                            {
                                text: 'Cancelar',
                                scope: this,
                                handler: this.destroy
                            }
                        ]
                    };
                    
                    toolkit.gfp.CSVContaCredito.superclass.constructor.call(this, cf);
                }
            }
        )
    }
)