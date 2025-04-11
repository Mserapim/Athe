Ext._define('rh.socialsecurity.RetirementPrevisionManage', {
    extend: 'toolkit.widget.TabPanel',

    getRetirementPrevisionGrid: function() {
        if(!this._retirementPrevisionGrid)
            this._retirementPrevisionGrid = Ext._create('rh.socialsecurity.RetirementPrevisionGrid', {
                hideItemsToolbar: ['add', 'remove'],
                columnAction: false,
                allowRemove: false,
                minHeight: 250,
                region: 'center'
            });

            this._retirementPrevisionGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();

                    if(selection.length > 0)
                        this.retirementPrevision(selection[0]);
                    else
                        this.retirementPrevision(null);
                }
            });

        return this._retirementPrevisionGrid;
    },

    retirementPrevision: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._retirementPrevision = value;

            if(dispatch)
                this.observeRetirementPrevision();
        }

        return this._retirementPrevision;
    },

    observeRetirementPrevision: function() {
        var value = this.retirementPrevision();

        if(value) {
            this.getEmploymentBondGrid().enable();
            this.getEmploymentBondGrid().setParam('retirement_prevision', value.get('pk'));
            this.getEmploymentBondGrid().setFilterProperty('retirement_prevision', value.get('pk'), 101);
            this.getEmploymentBondGrid().defaultValues({
                contributor_unicode: value.get('natural_person_unicode')
            });
        }
        else {
            this.getEmploymentBondGrid().disable();
            this.getEmploymentBondGrid().setParam('retirement_prevision', 0);
            this.getEmploymentBondGrid().setFilterProperty('retirement_prevision', 0, 101, false);
            this.getEmploymentBondGrid().getStore().removeAll();
            this.getEmploymentBondGrid().defaultValues({
                contributor_unicode: null
            });
        }
    },

    getEmploymentBondGrid: function(cfg) {
        if(!this._employmentBondGrid) {
            this._employmentBondGrid = Ext._create('rh.socialsecurity.EmploymentBondGrid', {
                title: 'Vínculos Empregatícios',
                region: 'south',
                gridAutoLoad: false,
                height: 290,
                minHeight: 250,
                split: true
            });
        }

        return this._employmentBondGrid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Previsão de Aposentadoria'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getRetirementPrevisionGrid(),
                    this.getEmploymentBondGrid()
                ]
            }
        );

        rh.socialsecurity.RetirementPrevisionManage.superclass.constructor.call(this, cfg);
        this.observeRetirementPrevision();
    }
});
