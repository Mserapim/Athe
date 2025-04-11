Ext._define('judicial.parts.DilationPeriodWindow', {
    extend: 'judicial.PartLawsuitHandLess',

    rest: 'judicial.parts.DilationPeriodRestful',

    width: 900,

    actionTitle: 'Registro de Dilação de Prazo',

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                title: 'Principal',
                border: false,
                items: [
                    {
                        xtype: 'ckeditor',
                        hideLabel: true,
                        name: 'justification',
                        height: 420
                    }
                ]
            });

        return this._mainPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        height: 550,
                        border: false,
                        items: [
                            this.getMainPanel(cfg),
                            this.getAttachementPanel(cfg)
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    dilationPeriod: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._dilationPeriod = value;

            if(dispatch)
                this.observeDilationPeriod();
        }

        return this._dilationPeriod;
    },

    observeDilationPeriod: function() {
        var value = this.dilationPeriod();

        if(value) {
            this.getAttachementPanel().enable();
            this.getAttachementPanel().setParam('attached_document', value);
            this.getAttachementPanel().setFilterProperty('attached_document', value, 100);
        }
        else {
            this.getAttachementPanel().disable();
            this.getAttachementPanel().setParam('attached_document', 0);
            this.getAttachementPanel().setFilterProperty('attached_document', 0, 100);
            this.getAttachementPanel().getStore().removeAll();
        }
    },

    getAttachementPanel: function(cfg) {
        if(!this._attachmentPanel)
            this._attachmentPanel = Ext._create('judicial.parts.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false,
                flex: 1
            });

        return this._attachmentPanel;
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
            console.info('lawsuit com valor');
        }
        else {
            console.info('undefined sem valor');
        }
    },

    readDataCallback: function(instance) {
        this.dilationPeriod(instance.pk);
        this.lawsuit(instance.lawsuit);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            buttonAlign: 'left',
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.readDataCallback(instance);
                    this.getFormPanel().getForm().setValues(instance);
                    this.action = 'update';
                    this.oId = instance.pk;
                }
            }
        });

        judicial.parts.DilationPeriodWindow.superclass.constructor.call(this, cfg);
        this.on({
            scope: this,
            render: function() {
                this.dilationPeriod(cfg.oId || null);
            }
        });
    }
});

judicial.PartLawsuitGrid.register('judicial.dilationperiod', 'judicial.parts.DilationPeriodWindow');
