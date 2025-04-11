
Ext._define('edocs.protocolo.box.GroupLocationDestinationGrid', {
    extend: 'edocs.protocolo.GroupGeneralOrganGrid',

    // mixins: {
    //     'MixinSelectionGrid': 'edocs.protocolo.box.MixinSelectionGrid'
    // },

    configOrderToolBar: ['addField', '-'],

    getAddField: function(cfg) {
        if(!this._addField)
            this._addField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Adicionar destinatário',
                rest: 'edocs.protocolo.GroupGeneralOrganRestful',
                emptyText: 'Selecione o item para adicionar a lista de destinatários',
                submitValue: false,
                comboListeners: {
                    scope: this,
                    select: function(combo, data) {
                        this.addSelection(data.get('pk'));
                        combo.clearValue();
                    }
                }
            });

        return this._addField;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                columnAction: true,
                selected: [],
                gridAutoLoad: false
            }
        );

        edocs.protocolo.box.GroupLocationDestinationGrid.superclass.constructor.call(this, cfg);

        this.setFilterProperty('pk__in', this.selected, 100);

        this.on({
            scope: this,
            render: function() {
                this.getAddFieldAction().setWidth(this.getBox().width - 15);
                this.getAddField().setWidth(this.getBox().width - 150);
            }
        });
    }
});

Ext.apply(
    edocs.protocolo.box.GroupLocationDestinationGrid.prototype,
    edocs.protocolo.box.MixinSelectionGrid
);
