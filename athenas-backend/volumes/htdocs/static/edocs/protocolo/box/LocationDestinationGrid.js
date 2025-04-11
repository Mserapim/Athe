
Ext._define('edocs.protocolo.box.LocationDestinationGrid', {
    extend: 'rh.workplace.Grid',

    configOrderToolBar: ['addField', '-'],

    hideColumns: [
        'executivo', 'data_alteracao', 'andar', 'esfera_governamental_display', 'comarca_unicode',
        'pai_unicode', 'job_position_responsible', 'designacao', 'order_nome', 'codigo',
        'instancia_unicode', 'publica_doc', 'entrancia_unicode', 'codigo_igeprev', 'poder_display',
        'abreviacao', 'sigla', 'localidade_unicode', 'acesso_protocolo_geral', 'ouvidoria', 'ativo',
        'code_cnmp', 'responsible_substituted_unicode', 'organizational_classification_display',
        'organograma', 'lotacionograma', 'habilita_protocolo', 'owner_unicode'
    ],

    getAddField: function(cfg) {
        if(!this._addField)
            this._addField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Adicionar destinatário',
                rest: 'rh.workplace.Restful',
                minChars: 2,
                emptyText: 'Selecione o item para adicionar a lista de destinatários',
                submitValue: false,
                preFilter: [
                    {
                        'property': 'ativo',
                        'value': true,
                        'stage': 0
                    },
                    {
                        'property': 'habilita_protocolo',
                        'value': true,
                        'stage': 1
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

        edocs.protocolo.box.LocationDestinationGrid.superclass.constructor.call(this, cfg);

        this.setFilterProperty('pk__in', this.selected, 100, false);
        this.addFilterProperty('ativo', true, 101);
        this.addFilterProperty('habilita_protocolo', true, 102);

        this.on({
            scope: this,
            render: function() {
                this.getAddFieldAction().setWidth(this.getBox().width - 15);
                this.getAddField().setWidth(this.getBox().width - 140);
            }
        });
    }
});

Ext.apply(
    edocs.protocolo.box.LocationDestinationGrid.prototype,
    edocs.protocolo.box.MixinSelectionGrid
);
