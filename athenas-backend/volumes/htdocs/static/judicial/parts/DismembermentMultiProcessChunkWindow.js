
Ext._define('judicial.parts.DismembermentMultiProcessChunkWindow', {
    extend: 'core.RestfulWindow',
    rest: 'judicial.parts.DismembermentMultiProcessChunkRestful',

    width: 600,

    getLegalMatterField: function(cfg) {
        if(!this._legalMatterField)
            this._legalMatterField = Ext._create('core.fields.RelatedRestfulField', {
                sourceRest: 'judicial.taxonomy.LegalMatterRestful',
                rest: this.rest,
                fieldLabel: 'Assuntos',
                name: 'matters',
                height: 250,
                width: 663
            });

        return this._legalMatterField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                    width: 465
                },
                items: [
                    {
                        allowBlank: false,
                        fieldLabel: "Novo Título",
                        name: "change_title",
                        xtype: "textfield"
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Assunto principal",
                        allowBlank: false,
                        rest: "judicial.taxonomy.LegalMatterRestful",
                        name: "main_matter",
                        gridConfig: {
                            columnAction: false,
                            allowUpdate: false,
                            allowRemove: false,
                            hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                        },
                    },
                    this.getLegalMatterField(cfg)
                ]
            });

        return this._formPanel;
    },

    chunk: function(value, prevent) {
        prevent = (prevent || false);

        if(value) {
            this._chunk = value;

            if(!prevent)
                this.observeChunk();
        }

        return this._chunk;
    },

    observeChunk: function() {
        var value = this.chunk();
        this.getLegalMatterField().objectId(value);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                disableSaveAndNew: true,
                saveAndContinue: {
                    scope: this,
                    fn: function(instance) {
                        this.oId = (instance || {}).pk;
                        this.getFormPanel().getForm().setValues(instance || {});
                        this.chunk((instance || {}).pk);
                        this.action = 'update';
                    }
                },
                border: false,
                title: 'Desmembramento de Procedimento'
            });

        judicial.parts.DismembermentMultiProcessChunkWindow.superclass.constructor.call(this, cfg);
        this.chunk(this.oId || null);
    }
});
