Ext._define('judicial.parts.AdjustmentLawsuitWindow', {
    extend: 'judicial.PartLawsuitActionWindow',

    rest: 'judicial.parts.AdjustmentLawsuitRestful',

    width: 800,

    autoCreate: true,

    getNewMattersField: function(cfg) {
        if(!this._newMattersField)
            this._newMattersField = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Outros assuntos',
                sourceRest: 'judicial.taxonomy.LegalMatterRestful',
                rest: this.rest,
                hideLabel: true,
                name: 'new_matters',
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                height: 400,
                border: false
            });

        return this._newMattersField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                items: [
                    {
                        allowBlank: true,
                        fieldLabel: "Título",
                        name: "new_title",
                        xtype: "textfield",
                        width: 650
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Área de atuação",
                        allowBlank: false,
                        rest: "judicial.params.ActingZoneRestful",
                        name: "new_acting_zone",
                        gridConfig: {
                            columnAction: false,
                            allowUpdate: false,
                            allowRemove: false,
                            hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                        },
                        preFilter: [
                            {property: 'enabled', value: 'on', stage: 1}
                        ]
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Assunto principal",
                        allowBlank: false,
                        rest: "judicial.taxonomy.LegalMatterRestful",
                        name: "new_main_matter",
                        gridConfig: {
                            columnAction: false,
                            allowUpdate: false,
                            allowRemove: false,
                            hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                        },
                    },
                    this.getNewMattersField()
                        
                ]
            });

        return this._formPanel;
    },

    readDataCallback: function(instance) {
        this.adjustmentLawsuit(instance.pk);
        this.getFormPanel().getForm().setValues(instance);
        this.getNewMattersField().disable();
        judicial.parts.AdjustmentLawsuitWindow.superclass.readDataCallback.call(this, instance);
    },

    adjustmentLawsuit: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._AdjustmentLawsuit = value;

            if(!prevent) this.observeAdjustmentLawsuit();
        }

        return this._AdjustmentLawsuit;
    },

    observeAdjustmentLawsuit: function() {
        var value = this.adjustmentLawsuit();

        this.getNewMattersField().objectId(value);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            border: false,
            buttonAlign: 'left',
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.adjustmentLawsuit(instance.pk);
                    this.getFormPanel().getForm().setValues(instance);

                }
            }
        });

        judicial.parts.AdjustmentLawsuitWindow.superclass.constructor.call(this, cfg);
        this.observeAdjustmentLawsuit();
    }
});

judicial.PartLawsuitGrid.register('judicial.adjustmentlawsuit', 'judicial.parts.AdjustmentLawsuitWindow');
