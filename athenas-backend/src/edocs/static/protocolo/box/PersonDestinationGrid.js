
Ext._define('edocs.protocolo.box.PersonDestinationGrid', {
    extend: 'rh.person.Grid',

    mixins: {
        'MixinSelectionGrid': 'edocs.protocolo.box.MixinSelectionGrid'
    },

    hideColumns: [ 'rate_fill' ],

    configOrderToolBar: ['addField', '-'],

    getAddField: function(cfg) {
        if(!this._addField)
            this._addField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Adicionar destinatário',
                rest: 'rh.person.Restful',
                emptyText: 'Selecione o item para adicionar a lista de destinatários',
                submitValue: false,
                preFilter: [
                    {
                        'property': 'enable_protocol',
                        'value': true,
                        'stage': 101
                    }
                ],
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

        edocs.protocolo.box.PersonDestinationGrid.superclass.constructor.call(this, cfg);

        this.setFilterProperty('pk__in', this.selected, 100);
        this.addFilterProperty('enable_protocol', true, 101);

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
    edocs.protocolo.box.PersonDestinationGrid.prototype,
    edocs.protocolo.box.MixinSelectionGrid
);
