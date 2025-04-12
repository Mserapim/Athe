
Ext._define('judicial.parts.DismembermentMultiProcessWindow', {
    extend: 'judicial.PartLawsuitActionWindow',

    rest: 'judicial.parts.DismembermentMultiProcessRestful',

    width: 800,

    autoCreate: true,

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

    readDataCallback: function(instance) {
        this.dismembermentMultiProcess(instance.pk);
    },

    getChunkGrid: function(cfg) {
        if(!this._chunkGrid) {
            this._chunkGrid = Ext._create('judicial.parts.DismembermentMultiProcessChunkGrid', {
                title: 'Desmembramentos',
                autoLoad: false
            });
        }

        return this._chunkGrid;
    },

    dismembermentMultiProcess: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._dismembermenMultitProcess = value;
            if(dispatch)
                this.observerDismembermentMultiProcess();
        }
        return this._dismembermenMultitProcess;
    },

    observerDismembermentMultiProcess: function() {
        var value = this.dismembermentMultiProcess();

        this.getLegalMatterField().objectId(value);

        if(value) {
            this.getChunkGrid().enable();
            this.getChunkGrid().setParam('dismemberment', value);
            this.getChunkGrid().setFilterProperty('dismemberment', value, 100);
        }
        else {
            this.getChunkGrid().disable();
            this.getChunkGrid().setParam('dismemberment', 0);
            this.getChunkGrid().setFilterProperty('dismemberment', 0, 100);
            this.getChunkGrid().getStore().removeAll();
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
                            this.getChunkGrid(cfg)
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
                        this.oId = (instance || {}).pk;
                        this.dismembermentMultiProcess((instance || {}).pk);
                        this.getFormPanel().getForm().setValues((instance || {}));
                        this.action = 'update';
                    }
                },
                border: false,
                title: 'Desmembramento de Procedimento'
            });

        judicial.parts.DismembermentMultiProcessWindow.superclass.constructor.call(this, cfg);
        this.observerDismembermentMultiProcess();
    }
});

judicial.PartLawsuitGrid.register('judicial.dismembermentmultiprocess', 'judicial.parts.DismembermentMultiProcessWindow');
