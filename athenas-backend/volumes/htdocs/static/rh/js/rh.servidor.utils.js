Ext.ns('toolkit.rh.servidor.utils');

Ext.apply(toolkit.rh.servidor.utils,{

        EfetivoFieldSet: Ext.extend(toolkit.rh.utils.CustomFieldSet,{
            constructor: function(args) {
                var cf = {
                    title: 'Efetivo',
                    collapsible: true,
                    collapsed: (args.cargo || args.progressao ? false : true),
                    autoWidth: true,
                    autoHeight: true,
                    labelAlign: 'left',
                    defaults: {anchor: '-20'},
                    defaultType: 'displayfield',
                    items: [
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Cargo',
                            value: args.cargo,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Progressão atual',
                            value: args.progressao,
                            readOnly: true
                        }
                    ]
                };
                toolkit.rh.servidor.utils.EfetivoFieldSet.superclass.constructor.call(this, cf);
            }
        }),

        ComissaoFieldSet: Ext.extend(toolkit.rh.utils.CustomFieldSet,{
            constructor: function(args) {
                var cf = {
                    title: 'Comissão/Função',
                    collapsible: true,
                    collapsed: (args.cargo || args.referencia ? false : true),
                    autoWidth:true,
                    autoHeight: true,
                    labelAlign: 'left',
                    defaults: {anchor: '-20'},
                    defaultType: 'displayfield',
                    items: [
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Cargo',
                            value: args.cargo,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Referência',
                            value: args.referencia,
                            readOnly: true
                        }
                    ]
                };
                toolkit.rh.servidor.utils.ComissaoFieldSet.superclass.constructor.call(this, cf);
            }
        }),

        DesignacaoFieldSet: Ext.extend(toolkit.rh.utils.GridNew,{
            constructor: function(args) {
                args.acoes = false;
                toolkit.rh.servidor.utils.DesignacaoFieldSet.superclass.constructor.call(this, args);
            }
        }),

        EletivoFieldSet: Ext.extend(toolkit.rh.utils.CustomFieldSet,{
            constructor: function(args) {
                var cf = {
                    title: 'Eletivo',
                    collapsible: true,
                    collapsed: (args.cargo ? false : true),
                    autoWidth:true,
                    autoHeight: true,
                    labelAlign: 'left',
                    defaults: {anchor: '-20'},
                    defaultType: 'displayfield',
                    items: [
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Cargo',
                            value: args.cargo,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Referência',
                            value: args.referencia,
                            readOnly: true
                        }
                    ]
                };
                toolkit.rh.servidor.utils.EletivoFieldSet.superclass.constructor.call(this, cf);
            }
        }),

        InformacoesFieldSet: Ext.extend(toolkit.rh.utils.CustomFieldSet,{
            constructor: function(args) {
                var cf = {
                    title: 'Informações',
                    collapsible: true,
                    collapsed: (args.cargo || args.situacao_funcional || args.lotacao || args.estagio_probatorio || args.data_estabilidade ? false : true),
                    autoWidth:true,
                    autoHeight: true,
                    labelAlign: 'left',
                    defaults: {anchor: '-20'},
                    defaultType: 'displayfield',
                    items: [
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Categoria',
                            value: args.categoria,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Situação Funcional',
                            value: args.situacao_funcional,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Lotação',
                            value: args.lotacao,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Estágio Probatório',
                            value: args.estagio_probatorio,
                            readOnly: true
                        },
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Estabilidade',
                            value: args.data_estabilidade,
                            readOnly: true
                        }
                    ]
                };
                toolkit.rh.servidor.utils.InformacoesFieldSet.superclass.constructor.call(this, cf);
            }
        })
});