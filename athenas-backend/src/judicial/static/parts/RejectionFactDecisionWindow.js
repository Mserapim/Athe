/**
 *
 **/
Ext._define('judicial.parts.RejectionFactDecisionWindow', {
    extend: 'Ext.Window',

    getDecisionTypeField: function(cfg) {
        if(!this._decisionTypeField)
            this._decisionTypeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Decisão',
                hiddenName: 'decision_type',
                width: 250,
                choiceId: 'judicial.DECISION_TYPE',
                listeners: {
                    scope: this,
                    select: function(combo, value) {
                        if(value.get('value') == 2) {
                            this.getOrdinaceTypeField().setValue(null);
                            this.getOrdinaceTypeField().disable();
                        }
                        else {
                            this.getOrdinaceTypeField().enable();
                        }
                    }
                }
            });

        return this._decisionTypeField;
    },

    getOrdinaceTypeField: function(cfg) {
        if(!this._ordinaceTypeField)
            this._ordinaceTypeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Instaurar Procedimento',
                hiddenName: 'type_ordinace',
                name: 'type_ordinace',
                width: 250,
                choiceId: 'judicial.TYPE_ORDINACE',
                disabled: true
            });

        return this._ordinaceTypeField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 130,
                items: [
                    this.getDecisionTypeField(),
                    this.getOrdinaceTypeField(),
                    {
                        hideLabel: true,
                        xtype: 'ckeditor',
                        name: 'decision_text',
                        height: 350
                    }
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Assinar',
                    scope: this,
                    handler: this.sign
                },
                '->',
                {
                    text: 'Salvar',
                    scope: this,
                    handler: this.save
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    sign: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Buscando informações...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('sign_decision', this.rejectionFactId, 'POST', {
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success)
                        Ext.Msg.show({
                            title: 'Assinando documento',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'Reconsideração assinda com sucesso!'
                        });
                    else
                        Ext.Msg.show({
                            title: 'Assinando',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Assinando documento',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento.'
                    });


                }
            })
        );
    },

    save: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Buscando informações...'});
        mask.show();
        rest.doRequest(
            rest.getRoute('store_decision', this.rejectionFactId, 'POST', {
                scope: this,
                params: this.getFormPanel().getForm().getValues(),
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        Ext.Msg.show({
                            title: 'Persistindo reconsideração',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'Dados persistidos com sucesso.'
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Persistindo reconsideração',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Persistindo reconsideração',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento'
                    });
                }
            })
        );
    },

    factoryRestful: function() {
        return Ext._create('judicial.parts.RejectionFactRestful');
    },

    loadData: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Buscando informações...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('read', this.rejectionFactId, 'GET', {
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.getFormPanel().getForm().setValues(rst.instance);

                        if(rst.instance.decision_type == 2) {
                            this.getOrdinaceTypeField().setValue(null);
                            this.getOrdinaceTypeField().disable();
                        }
                    }
                    else
                        this.getFormPanel().disable();
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Buscando informações',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento.'
                    });

                    this.close();
                }
            })
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Indeferimento de Notícia de Fato',
                width: Ext.getBody().getBox().width * 0.9
            }
        );

        if(!cfg.rejectionFactId)
            throw 'Deve ser passado o identificador do Indeferimento de Notícia de Fato.';

        Ext.apply(
            cfg,
            {
                height: 600,
                buttonAlign: 'left',
                buttons: this.getButtons(cfg),
                items: [
                    this.getFormPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.parts.RejectionFactDecisionWindow.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            render: function() {
                var me = this;

                setTimeout(
                    function() {
                        me.loadData();
                    },
                    250
                );
            }
        });
    }
});
