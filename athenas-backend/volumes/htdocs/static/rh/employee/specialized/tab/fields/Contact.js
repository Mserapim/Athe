rh.employee.specialized.tab.fields.Contact = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Contact.superclass.constructor.call(this, cfg);
        },

        observerNaturalPersonPk: function(){
            rh.employee.specialized.tab.fields.Contact.superclass.observerNaturalPersonPk.call(this, {});
            if(this.myParams('naturalPersonPk')){
                this.getAddressGrid().setParam('person', this.myParams('naturalPersonPk'));
                this.getAddressGrid().setFilterProperty('person__id', this.myParams('naturalPersonPk'), 100);
                this.getAddressGrid().enable();
                this.getPhoneGrid().setParam('person', this.myParams('naturalPersonPk'));
                this.getPhoneGrid().setFilterProperty('person__id', this.myParams('naturalPersonPk'), 100);
                this.getPhoneGrid().enable();
                
                this.getPhoneEmergencyGrid().setParam('emergency_type', this.myParams('emergency_type'));
                this.getPhoneEmergencyGrid().setParam('person', this.myParams('naturalPersonPk'));
                this.getPhoneEmergencyGrid().setFilterProperty('person__id', this.myParams('naturalPersonPk'), 100);
                this.getPhoneEmergencyGrid().enable();
            }else{
                this.getAddressGrid().setParam('person', undefined);
                this.getAddressGrid().removeFilterProperty('person__id', 100, false);
                this.getAddressGrid().disable();

                this.getPhoneGrid().setParam('person', undefined);
                this.getPhoneGrid().removeFilterProperty('person__id', 100, false);
                this.getPhoneGrid().disable();

                this.getPhoneEmergencyGrid().setParam('emergency_type', this.myParams('emergency_type'));
                this.getPhoneEmergencyGrid().setParam('person', this.myParams('naturalPersonPk'));
                this.getPhoneEmergencyGrid().setFilterProperty('person__id', this.myParams('naturalPersonPk'), 100);
                this.getPhoneEmergencyGrid().enable();
                
            }
        },

        fields: function(cfg){
            return [
                this.getAddressGrid({}, {}),
                this.getPhoneGrid({}, {}),
                this.getPhoneEmergencyGrid({},{}),
           
            ];
        },

        getAddressGrid: function(cfgPanel, cfg) {
            cfg = core.nullValue(cfg, {});
            if(!this._addressGrid){
                Ext.applyIf(
                    cfg,
                    {
                        hideItemsToolbar: ['search', 'download'],
                        title: 'Endereço',
                        region: 'center',
                        border: false,
                        scope: this,
                        height: 250,
                        columnAction: false,
                        gridAutoLoad: false,
                    }
                );
                this._addressGrid = Ext._create('rh.endereco.EnderecoGrid', cfg);
            }
            return this._addressGrid;
        },

        getPhoneGrid: function(cfgPanel, cfg) {
            cfg = core.nullValue(cfg, {});
            if(!this._phoneGrid){
                Ext.applyIf(
                    cfg,
                    {
                        hideItemsToolbar: ['search', 'download'],
                        title: 'Telefones',
                        region: 'north',
                        border: false,
                        scope: this,
                        height: 230,
                        columnAction: false,
                        gridAutoLoad: false,
                    }
                );
                this._phoneGrid = Ext._create('rh.telefone.TelefoneGrid', cfg);
            }
            return this._phoneGrid;
        },

        getPhoneEmergencyGrid: function(cfgPanel, cfg) {
            cfg = core.nullValue(cfg, {});
            if(!this._phoneEmergencyGrid){
                Ext.applyIf(
                    cfg,
                    {
                        hideItemsToolbar: ['search', 'download'],
                        title: 'Telefones de Emergência',
                        region: 'north',
                        border: false,
                        scope: this,
                        height: 230,
                        columnAction: false,
                        gridAutoLoad: false,
                    }
                );
                this._phoneEmergencyGrid = Ext._create('rh.telefone.emergency.Grid', cfg);
            }
            return this._phoneEmergencyGrid;
        },
    }
);
