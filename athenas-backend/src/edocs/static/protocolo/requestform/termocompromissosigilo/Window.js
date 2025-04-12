Ext._define('edocs.protocolo.requestform.termocompromissosigilo.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFTermoCompromissoSigilo',

    rest: 'edocs.protocolo.requestform.termocompromissosigilo.Restful',

    width: 900,

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 90,
            items: [
                this.getCodeField(cfg),
                {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 2.75,
                            items: this.getHomeCourtField(cfg)
                        },
                        {
                            xtype: 'container',
                            style: 'margin-left: 15px',
                            layout: 'form',
                            flex: 1.25,
                            labelWidth: 30,
                            items: this.getDocumentTypeField('TERMO')  // mixin
                        },
                    ],
                },
                this.getSubjectField(cfg, {
                    value: 'TERMO DE COMPROMISSO DE MANUTENÇÃO DO SIGILO',
                    readOnly: true,
                }),
                this.getControlContainer(cfg),
            ],
        });

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (this._formPanel) {
            return this._formPanel;
        }

        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            items: this.getMainPanel(cfg),
        });

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Termo de Compromisso de Manutenção do Sigilo',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.termocompromissosigilo.Window',
    specialType: 'termocompromissomanutencaosigilo',
    group: 'Sigilo'
});
