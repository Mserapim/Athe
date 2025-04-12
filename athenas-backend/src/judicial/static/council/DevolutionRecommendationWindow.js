
Ext._define('judicial.council.DevolutionRecommendationWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.council.DevolutionRecommendationRestful',

    width: 800,


    getDevolutionToField: function(cfg) {
        if(!this._devolutionToField)
            this._devolutionToField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Devolver para',
                hiddenName: 'devolution_to',
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    autoLoad: false,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('EJudOutCourtLawsuit', 'my_tracks_executionorgan'),
                        method: 'GET'
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'pk', type: 'int'},
                            {name: 'description', type: 'string'},
                        ]
                    })
                }),
                width: 600,
                allowBlank: true
            });

        return this._devolutionToField;
    },


    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel',{
                title: 'Justificativa',
                items: [
                    {
                        xtype: 'ckeditor',
                        height: 449,
                        name: 'justification'
                    }
                ]
            });
        return this._mainPanel;
    },

    readDataCallback: function(instance) {
        this.attachments(instance.pk);
    },

    getAttachmentPanel: function(cfg) {
        if(!this._attachmentPanel)
            this._attachmentPanel = Ext._create('judicial.parts.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false
            });

        return this._attachmentPanel;
    },

    attachments: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._attachments = value;
            if(dispatch)
                this.observerAttachments();
        }
        return this._attachments;
    },


    observerAttachments: function() {
        var value = this.attachments();
        if(value) {
            this.getAttachmentPanel().enable();
            this.getAttachmentPanel().setParam('attached_document', value);
            this.getAttachmentPanel().setFilterProperty('attached_document', value, 100);
        }
        else {
            this.getAttachmentPanel().disable();
            this.getAttachmentPanel().setParam('attached_document', 0);
            this.getAttachmentPanel().setFilterProperty('attached_document', 0, 100);
            this.getAttachmentPanel().getStore().removeAll();
        }

    },


    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getDevolutionToField(cfg),
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        height: 580,
                        items: [
                            this.getMainPanel(),
                            this.getAttachmentPanel()
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    sign: function() {
        var rest = this.factoryRestful();

        rest.doRequest(
            rest.getRoute('sign', this.oId, 'PUT', {
                scope: this,
                success: function(xhr) {
                    rst = Ext.decode(xhr.responseText);

                    if(rst.success)
                        Ext.Msg.show({
                            title: 'Assinando documento',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'Documento assinado com sucesso.'
                        });
                    else
                        Ext.Msg.show({
                            title: 'Assinando documento',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Assinando o documento',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'O sistema esta indisponível neste momento.'
                    });
                }
            })
        );
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Assinar',
                    scope: this,
                    handler: this.sign,
                    handle: this.sign
                },
                '->'
            ].concat(judicial.council.DevolutionRecommendationWindow.superclass.getButtons.call(this, cfg));

        return this._buttons;
    },

    lawsuit: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._lawsuit = value;

            if(dispatch)
                this.observeLawsuit();
        }

        return this._lawsuit;
    },

    observeLawsuit: function() {
        var value = this.lawsuit();

        if(value) {
            this.getDevolutionToField().enable();
            this.getDevolutionToField().getStore().baseParams.pk=value;
            this.getDevolutionToField().getStore().load();
        }
        else {
            this.getDevolutionToField().disable();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                buttonAlign: 'left',
                disableSaveAndNew: true,
                saveAndContinue: {
                    scope: this,
                    fn: function(instance) {
                        this.oId = instance.pk;
                        this.attachments(instance.pk);
                        this.action = 'update';
                    }
                },
                border: false,
                title: 'Devolução com Recomendação'
            });

        judicial.council.DevolutionRecommendationWindow.superclass.constructor.call(this, cfg);
        this.observerAttachments();
        this.lawsuit((this.params || {}).lawsuit);
    }
});

judicial.PartLawsuitGrid.register('council.devolutionrecommendation', 'judicial.council.DevolutionRecommendationWindow');
