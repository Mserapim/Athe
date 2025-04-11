

Ext._define('rh.teletrabalho.RelatorioWindow', {
    extend: 'Ext.Window',

    PDF_RELATORIO: 'generate_report_pdf',
    CSV_RELATORIO: 'generate_report_csv',
    XLS_RELATORIO: 'generate_report_xls',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getTipoPedido(cfg),
                    this.getTipoAto(cfg),
                    {
                        xtype: 'fieldset',
                        title: 'Período data início',
                        width: 300,
                        layout: 'hbox',
                        items: [
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getPeriodoIniDtInicio(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getPeriodoIniDtFim(cfg),
                                ]
                            }
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Período data fim',
                        width: 300,
                        layout: 'hbox',
                        items: [
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getPeriodoFimDtInicio(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout:'form',
                                labelAlign:'top',
                                flex:'1',
                                width:150,
                                items:[
                                    this.getPeriodoFimDtFim(cfg),
                                ]
                            }
                        ]
                    },
                ]
                    
            });
        return this._formPanel;
    },

    getTipoPedido: function(cfg) {
        if(!this._tipoPedido)
            this._tipoPedido = Ext._create('core.fields.ComboField', {
                width: 200,
                name: 'tipo_pedido',
                hiddenName: 'tipo_pedido',
                fieldLabel: 'Tipo Pedido',
                store: [
                    [ 1, 'Adesão'],
                    [ 2, 'Prorrogação'],
                    [ 3, 'Ampliação'],
                    [ 9999, 'Todos'],
                ],
                triggerAction: 'all',
                value: 9999,
            });

        return this._tipoPedido;
    },

    getTipoAto: function(cfg) {
        if(!this._tipoAto)
            this._tipoAto = Ext._create('core.fields.ComboField', {
                width: 200,
                name: 'tipo_ato',
                hiddenName: 'tipo_ato',
                fieldLabel: 'Tipo Ato',
                store: [
                    [ 862, 'ATO 862/2019'],
                    [ 1058, 'ATO 1058/2021'],
                    [ 1149, 'ATO 1.149/2022'],
                    [ 9999, 'Todos'],
                ],
                triggerAction: 'all',
                value: 9999,
            });

        return this._tipoAto;
    },

    getPeriodoIniDtInicio: function(cfg) {
        if(!this._proceDataInicio)
            this._proceDataInicio = Ext._create('Ext.form.DateField', {
                hiddenName: 'periodo_inicio_data_inicio',
                fieldLabel: 'Início',
                allowBlank: true,
            });

        return this._proceDataInicio;
    },

    getPeriodoIniDtFim: function(cfg) {
        if(!this._proceDataFim)
            this._proceDataFim = Ext._create('Ext.form.DateField', {
                hiddenName: 'periodo_inicio_data_fim',
                fieldLabel: 'Fim',
                allowBlank: true,
            });

        return this._proceDataFim;
    },

    getPeriodoFimDtInicio: function(cfg) {
        if(!this._faltaDataInicio)
            this._faltaDataInicio = Ext._create('Ext.form.DateField', {
                hiddenName: 'periodo_fim_data_inicio',
                fieldLabel: 'Início',
                allowBlank: true,
            });

        return this._faltaDataInicio;
    },

    getPeriodoFimDtFim: function(cfg) {
        if(!this._faltaDataFim)
            this._faltaDataFim = Ext._create('Ext.form.DateField', {
                hiddenName: 'periodo_fim_data_fim',
                fieldLabel: 'Fim',
                allowBlank: true,
            });

        return this._faltaDataFim;
    },

    gerarRelatorio: function(tipo_relatorio){
        var form = this.getFormPanel().getForm();
        var p_ini_dt_ini = ''
        var p_ini_dt_fim = ''
        var p_fim_dt_ini = ''
        var p_fim_dt_fim = ''
        var msg_erro = ''

        if (this.getPeriodoIniDtInicio().getValue() != '') {
            p_ini_dt_ini = this.getPeriodoIniDtInicio().getValue().format('Y-m-d')
        }
        if (this.getPeriodoIniDtFim().getValue() != '') {
            p_ini_dt_fim = this.getPeriodoIniDtFim().getValue().format('Y-m-d')
        }
        if (this.getPeriodoFimDtInicio().getValue() != '') {
            p_fim_dt_ini = this.getPeriodoFimDtInicio().getValue().format('Y-m-d')
        }
        if (this.getPeriodoFimDtFim().getValue() != '') {
            p_fim_dt_fim = this.getPeriodoFimDtFim().getValue().format('Y-m-d')
        }
        
        if ((p_ini_dt_ini && p_ini_dt_fim) && p_ini_dt_ini > p_ini_dt_fim) {
            msg_erro = 'Data iníco do Período data início deve ser maio que data fim!'
        }
        if ((p_fim_dt_ini && p_fim_dt_fim) && p_fim_dt_ini > p_fim_dt_fim) {
            msg_erro = 'Data iníco do Período data fim deve ser maio que data fim!'
        }

        if (msg_erro == '') {
            var params = {
                tipo_pedido: this.getTipoPedido().getValue(),
                tipo_ato: this.getTipoAto().getValue(),
                p_ini_dt_ini: p_ini_dt_ini,
                p_ini_dt_fim: p_ini_dt_fim,
                p_fim_dt_ini: p_fim_dt_ini,
                p_fim_dt_fim: p_fim_dt_fim,
            };

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                   'RHGestorTeletrabalho', 
                   tipo_relatorio
                ),
                params: params,
                scope: this,
                success: function (request) {
                    var obj = Ext.decode(request.responseText);
                    if (obj.success){
                        Ext.Msg.show({
                            title: 'Solicitando Relatório',
                            msg: obj.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                        this.destroy();
                    }else{
                        Ext.Msg.show({
                            title: 'Error',
                            msg: obj.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }     
                },
                failure: function (request) {
                    Ext.Msg.show({
                        msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },
                scope: this
            });
        } else {
            Ext.Msg.show({
                title: 'Error',
                msg: msg_erro,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Relatório de Teletrabalho',
        		closable: true,
				height: 360,
        		width: 350
        	}
        );
		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				],
                buttons: [
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        menu: {
                            scope: this,
                            items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function(item) {
                                        this.gerarRelatorio(this.PDF_RELATORIO);
                                    }
                                },
                                {
                                    text: 'Arquivo CSV',
                                    type: 'CSV',
                                    iconCls: 'icon-ged icon-ged-text-csv',
                                    scope: this,
                                    handler: function(item) {
                                        this.gerarRelatorio(this.CSV_RELATORIO);
                                    }
                                },
                                {
                                    text: 'Arquivo XLS',
                                    type: 'XLS',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function(item) {
                                        this.gerarRelatorio(this.XLS_RELATORIO);
                                    }
                                },
                            ]
                        }
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);
		rh.teletrabalho.RelatorioWindow.superclass.constructor.call(this, cfg);
    }
});