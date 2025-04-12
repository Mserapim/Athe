Ext._define('corregedoria.linkinspectionraf.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.linkinspectionraf.Restful',

    width: 530,

    getItemField: function() {
        if(!this._itemField) {
            this._itemField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Item',
                allowBlank: true,
                rest: "raf.item.Restful",
                name: "raf_item",
                disabled: false,
                gridColumnAction: false,
                preFilter: [
                    {property: 'activated', value: 'True', stage: 100},
                    {property: 'quiz__activated', value: 'True', stage: 101},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['icons', 'typesubitem_display', 'number_order', 'actions'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._itemField;
    },

    getSubitemField: function() {
        if(!this._subitemField) {
            this._subitemField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Subitem',
                allowBlank: true,
                rest: "raf.subitem.Restful",
                name: "raf_subitem",
                gridColumnAction: false,
                preFilter: [
                    {property: 'activated', value: 'True', stage: 100},
                    {property: 'quiz__activated', value: 'True', stage: 101},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['icons', 'typesubitem_display', 'number_order', 'actions'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._subitemField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 55,
                        items: [
                            {
                                xtype: 'choicefield',
                                fieldLabel: 'Tabela',
                                hiddenName: 'inspection_table',
                                width: 440,
                                choiceId: 'corregedoria.INSPECTION_TABLE',
                            },
                            this.getItemField(),
                            this.getSubitemField(),
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
