Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationAgreementParameterWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.agreement.Restful',

    width: 500,

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            modal: true
        });

        Ext.apply(cfg, {
            title: 'Contratar',
            buttons: this.getButtons(cfg),
            items: [
                this.getFormPanel(cfg)
            ]
        });

        planning.hiring.minutesolicitationmanager.MinuteSolicitationAgreementParameterWindow.superclass.constructor.call(this, cfg);
    },

    generateAgreement: function() {
        Ext.Msg.show({
            title: 'Criando contrato',
            msg: 'Tem certeza que deseja criar um novo contrato?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if (btn === 'no') return;

                this._generateAgreement();
            }
        });
    },

    _generateAgreement: function() {
        var rest = Ext._create('planning.hiring.agreement.Restful');
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Criando contrato...' });
        var grid = this.grid;

        mask.show();
        rest.generateFromSolicitations(
            this.solicitations,
            this.getFormPanel().getForm().getValues(),
            {
                scope: this,
                fn: function(rst) {
                    grid.getStore().reload();
                    Ext.Msg.show({
                        title: 'Criando contrato',
                        msg: 'O contrato foi criado com sucesso. Deseja abrir o contrato para edição?',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function(btn) {
                            if(btn === 'yes') {
                                agreeWindow = Ext._create('planning.hiring.agreement.Window', {
                                    action: 'update',
                                    oId: rst.instance.pk,
                                    values: 'remote'
                                });

                                agreeWindow.tipo_contrato = 6;

                                agreeWindow.observeContrato();

                                agreeWindow.show();
                            }

                            this.close();
                        }
                    });
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Criando contrato',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Criar',
                    scope: this,
                    handler: function() { this.generateAgreement(); }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close() }
                }
            ];

        return this._buttons;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 350,
                        allowBlank: false,
                        fieldLabel: "Número",
                        name: "numero_contrato",
                        xtype: "textfield",
                    },
                    {
                        width: 350,
                        allowBlank: false,
                        fieldLabel: "Tipo de Contrato",
                        name: "TIPO_CONTRATO",
                        choiceId: "contrato.TIPO_CONTRATO",
                        xtype: "choicefield",
                        hiddenName: "tipo_contrato",
                        preFilter: [
                            {property: 'cvalue__in', value: ['6', '9'], stage: 1002}
                        ],
                    },
                    {
                        width: 350,
                        allowBlank: false,
                        fieldLabel: "Inicio da Vigência",
                        name: "data_inicio",
                        xtype: "datefield"
                    },
                    {
                        width: 350,
                        allowBlank: false,
                        fieldLabel: "Fim da Vigência",
                        name: "data_fim",
                        xtype: "datefield"
                    },
                    {
                        width: 350,
                        allowBlank: true,
                        fieldLabel: 'Copiar fiscais',
                        name: 'copiar_fiscais',
                        xtype: "checkbox"
                    }
                ]
            });
        return this._formPanel;
    },
});
