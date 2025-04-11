Ext._define('rh.gestorbatida.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getServidorGrid: function(cfg) {
        if(!this._servidor) {
            this._servidor = Ext._create('rh.gestorbatida.servidor.Grid', {
                region: 'north', 
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                height: 200,
                split: true,
            });

            this._servidor.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.observe(cfg, record);
                },
            });
        }

        return this._servidor;
    },


    getGestorBatidaGrid: function(cfg) {
        if(!this._subGestorBatidaGrid) {
            this._subGestorBatidaGrid = Ext._create('rh.gestorbatida.gestor_batidas.Grid', {
                gridAutoLoad: false,
                region: 'center',
                disabled: true,
                flex: 1.0,
                border: false,
                columnAction: false,
                observeFn: this.observe.bind(this),
                doubleClickHandler: function () { }

            });
        }

        return this._subGestorBatidaGrid;
    },


    observe: function(cfg, record, prevent) {
        prevent = core.nullValue(prevent, false);

        if (record !== undefined) {
            var effectiveUnicode = record.get('effective_unicode');
            var commissionUnicode = record.get('commission_unicode');

            var employeeCargo;
            if (effectiveUnicode) {
                employeeCargo = effectiveUnicode;
            } else if (commissionUnicode) {
                employeeCargo = commissionUnicode;
            } else {
                employeeCargo = 'Não encontrado';
            }

            var simplifiedRecord = {
                employee_id: record.get('servidor_pk'),
                employee_nome: record.get('pessoa_fisica_unicode'),
                employee_tipo: record.get('type_by_possession_display'),
                employee_matricula: record.get('matricula'),
                employee_cargo: employeeCargo,
                employee_lotacao: record.get('lotacao'),
                jornada_trabalho: record.get('jornada_trabalho'),
                duracao: record.get('duracao'),
            };
    
            this._servidorRecord = simplifiedRecord;
    
    
            if (!prevent)
                this.observeBatida(cfg);
            
        }
    
        return this._servidorRecord;
    },


    observeBatida: function(cfg){

        var record = this.observe();
        if (record && record.employee_id) {
            var grid = this.getGestorBatidaGrid(cfg);
            grid.enable();
            grid.servidor = record;
            
            grid.setFilterProperty('employee_id', record.employee_id, 0, false);
        
            var batidaGrid = this.getGestorBatidaGrid(cfg);
            var now = new Date();
            var firstDayOfMonth = Ext.util.Format.date(new Date(now.getFullYear(), now.getMonth(), 1), 'Y-m-d');
            var lastDayOfMonth = Ext.util.Format.date(new Date(now.getFullYear(), now.getMonth() + 1, 0), 'Y-m-d');
            if (batidaGrid._startDateFilter) {
                batidaGrid._startDateFilter.setValue(firstDayOfMonth);
            }
            if (batidaGrid._endDateFilter) {
                batidaGrid._endDateFilter.setValue(lastDayOfMonth);
            }
    
            batidaGrid.setFilterProperty('marcacao__date__gte', firstDayOfMonth, 1003, true);
            batidaGrid.setFilterProperty('marcacao__date__lte', lastDayOfMonth, 1004, true); 

            batidaGrid.setFilterProperty('marcacao_valida__in', [true], 1005, true);

            batidaGrid.getStore().load();
        } else {
            var grid = this.getGestorBatidaGrid(cfg);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Batidas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getServidorGrid(cfg),
                    

                    {

                        region: 'center',
                        layout: 'border',
                        minHeight: 150,
                        scope: this,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },

                        items: [
                            this.getGestorBatidaGrid(cfg),
                        ]
                    }

                ]
            }
        );

        rh.gestorbatida.Manage.superclass.constructor.call(this, cfg);
    }
});
