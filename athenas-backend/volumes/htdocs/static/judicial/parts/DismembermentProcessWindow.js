
Ext._define('judicial.parts.DismembermentProcessWindow', {
    extend: 'judicial.PartLawsuitWindow',

    rest: 'judicial.parts.DismembermentProcessRestful',

    width: 800,

    getLegalMatterField: function(cfg) {
        if(!this._legalMatterField)
            this._legalMatterField = Ext._create('core.fields.RelatedRestfulField', {
                sourceRest: 'judicial.taxonomy.LegalMatterRestful',
                rest: this.rest,
                fieldLabel: 'Assuntos',
                name: 'matters',
                height: 158,
                width: 663
            });

        return this._legalMatterField;
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel',{
                title: 'Justificativa',
                items: [
                    {
                        xtype: 'panel',
                        frame: true,
                        layout: 'form',
                        items: [
                            {
                                name: 'change_title',
                                xtype: 'textfield',
                                fieldLabel: 'Título',
                                width: 660
                            },
                            this.getLegalMatterField(cfg)
                        ]
                    },
                    {
                        xtype: 'container',
                        items: [
                            {
                                xtype: 'ckeditor',
                                height: 248,
                                name: 'justification'
                            }
                        ]
                    }
                ]
            });
        return this._mainPanel;
    },

    readDataCallback: function(instance) {
        this.dismembermentProcess(instance.pk);
    },

    getAttachmentPanel: function(cfg) {
        if(!this._attachmentPanel)
            this._attachmentPanel = Ext._create('judicial.parts.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false
            });

        return this._attachmentPanel;
    },

    dismembermentProcess: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._dismembermentProcess = value;
            if(dispatch)
                this.observerDismembermentProcess();
        }
        return this._dismembermentProcess;
    },

    observerDismembermentProcess: function() {
        var value = this.dismembermentProcess();

        this.getLegalMatterField().objectId(value);

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
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        height: 580,
                        border: false,
                        items: [
                            this.getMainPanel(),
                            this.getAttachmentPanel()
                        ]
                    }
                ]
            });

        return this._formPanel;
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
                        this.dismembermentProcess(instance.pk);
                        this.getFormPanel().getForm().setValues(instance);
                        this.action = 'update';
                    }
                },
                border: false,
                title: 'Desmembramento de Procedimento'
            });

        judicial.parts.DismembermentProcessWindow.superclass.constructor.call(this, cfg);
        this.observerDismembermentProcess();
    }
});

judicial.PartLawsuitGrid.register('judicial.dismembermentprocess', 'judicial.parts.DismembermentProcessWindow');
