Ext._define('rh.gratifications_manager.diligence.gratificacao.Window', {
    extend: 'core.RestfulWindow',

    width: 900,
    height: 300,

    constructor: function(cfg) {
        this.gratDiligenciaId = cfg.gratDiligenciaId;

        Ext.apply(
            cfg,
            {
                listeners: {
                    scope: this,
                    render: function() {
                        this.readData();
                    }
                },
            }
        );

        rh.gratifications_manager.diligence.gratificacao.Window.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false
            });

        return this._formPanel;
    },

    getParams: function() {
        return core.nullValue(this.params, {});
    },

    save: function() {
        var form = this.getFormPanel().getForm();
        var rest = Ext._create('rh.gratifications_manager.diligence.gratificacao.Restful');
        var cfg = {
            externalCallback: this._prepareSuccessCallback(this.callback, close),
            params: Ext.applyIf(
                form.getValues(),
                this.getParams()
            )
        };

        rest.update(
            this.gratDiligenciaId,
            cfg,
            {
                el: this.getEl(),
                waitMessage: 'Persistindo os dados.'
            }
        );

        this.getStore().reload();
    },

    readData: function() {
        var rest = Ext._create('rh.gratifications_manager.diligence.gratificacao.Restful');

        rest.get(
            this.gratDiligenciaId,
            {
                success: {
                    scope: this,
                    fn: function(instance) {
                        this.getFormPanel().getForm().setValues(instance);
                    }
                }
            },
            {
                el: this.getEl(),
                msg: 'carregando...'
            }
        );
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            this._buttons.push({
                text: 'Salvar',
                scope: this,
                handler: function() { this.save(); }
            });

            this._buttons.push(
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            );
        }

        return this._buttons;
    },

    getFormPanel: function(cfg_window, cfg) {
        if(!this._formPanel){
            cfg = core.nullValue(cfg, {});

            Ext.apply(
                cfg,
                {
                    border: false,
                    height: 300,
                    items: [
                        this.getTabPanel(cfg, cfg_window),
                    ]
                }
            );
            
            this._formPanel = Ext._create('Ext.form.FormPanel', cfg);
        }
        return this._formPanel;
    },

    getTabPanel: function(cfg_window, cfg) {
        if(!this._tabPanel){
            cfg = core.nullValue(cfg, {});
            
            Ext.apply(
                cfg,
                {
                    border: false,
                    activeTab: 0,
                    frame: true,
                    layout: 'form',
                    height: this.tabPanelHeight,
                    title: 'Dados',
                    items: [
                        this.getPanelInformationItems(cfg_window),
                    ]
                }
            );
            
            this._tabPanel = Ext._create('Ext.Panel', cfg);
        }
        return this._tabPanel;
    },

    getPanelInformationItems: function(cfg_window){
        return [
            {
                xtype: "textfield",
                fieldLabel: "Período",
                name: "periodo",
                disabled: true,
                width: 380,
            },
            {
                xtype: "textfield",
                fieldLabel: "Titular",
                name: "titular",
                disabled: true,
                width: 380,
            },
            {
                xtype: "textfield",
                fieldLabel: "Substituto",
                name: "substituto",
                disabled: true,
                width: 380,
            },
            {
                xtype: "textfield", 
                fieldLabel: "Gratificação", 
                name: "evento_unicode",
                disabled: true,
                width: 380,
            },
            {
                fieldLabel: "Dias Consolidado - Titular",
                name: "qtd_dias_consolidado_titular",
                xtype: "textfield",
                disabled: true,
                width: 150,
            },
            {
                fieldLabel: "Dias Deferido - Titular",
                name: "qtd_dias_deferido_titular",
                xtype: "textfield",
                allowBlank: true,
                width: 150,
            },
            {
                fieldLabel: "Dias Consolidado - Substituto",
                name: "qtd_dias_consolidado_substituto",
                xtype: "textfield",
                disabled: true,
                width: 150,
            },
            {
                fieldLabel: "Dias Deferido - Substituto",
                name: "qtd_dias_deferido_substituto",
                xtype: "textfield",
                allowBlank: true,
                width: 150,
            },
        ]
    },

});