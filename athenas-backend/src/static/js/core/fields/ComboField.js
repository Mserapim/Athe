/**
 *
 **/
Ext._define('core.fields.ComboField', {
    extend: 'Ext.form.ComboBox',

    xtype: 'rest-combofield',

    factoryRestful: function() {
        return Ext._create(this.rest);
    },

    setStore: function(store) {
        this._store = store;
        this.bindStore(this._store);
    },

    getStore: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if (!this.store)
            this.store = this.factoryRestful().getStore(core.nullValue(cfg.autoLoad, false));

        if (cfg.preFilter)
            this.setPreFilter(cfg.preFilter);

        return this.store;
    },

    setPreFilter: function(preFilter) {
        this.preFilter = preFilter;

        this.getStore().baseParams.filter = Ext.encode(
            core.nullValue(this.preFilter, [])
        );
    },

    setValue: function(value, trigged) {
        var fireSelect = function(cmb, value) {
            var index = cmb.getStore().findExact(cmb.valueField, value, null);
            var record = cmb.getStore().getAt(index);
            var valid = (record !== undefined);

            // console.debug('COMBO SET VALUE('+ (record !== undefined) +'): '+cmb.startValue+'/'+record.id);
            if(valid)
                cmb.fireEvent('select', cmb, record, index, true);

        };

        //

        var changedValid = function(cmb, value){
            var index = cmb.getStore().findExact(cmb.valueField, value, null);
            var record = cmb.getStore().getAt(index);
            var valid = (record !== undefined);

            // console.debug('OV: '+cmb.value+' NV: '+value+' ORV:'+cmb.originalValue+' SV: '+cmb.startValue+' VALID: '+valid);

            if(!record || cmb.startValue != record.get(cmb.valueField))
                cmb.fireEvent('changevalid', cmb, cmb.getValue(), cmb.startValue, valid);
        };

        trigged = core.nullValue(trigged, false);

        if(!isNaN(value) && value !== '')
            try {
                value = Ext.decode(value);
            }
            catch(e) {}

        if(this.getStore().findExact(this.valueField, value, null) >= 0 || trigged) {
            if(this.getStore().findExact(this.valueField, value, null) >= 0 && value !== '') {
                core.fields.ComboField.superclass.setValue.call(this, value);
                fireSelect(this, value);
            }
            else {
                core.fields.ComboField.superclass.setValue.call(this, '');
                this.markInvalid('O valor não existe para ser relacionado.');
            }
        }
        else if(!trigged && (value !== '' && value)) {
            var store = this.getStore();
            var baseFilter = Ext.decode(store.baseParams.filter || '[]');

            if(store.baseParams.keyword)
                store.baseParams.keyword = undefined;

            var stage = 1;
            var flag;

            do {
                flag = true;

                baseFilter.forEach(
                    function(filter) {
                        if(stage === (filter.stage || 1)) {
                            stage +=1;
                            flag = false;
                        }
                    }
                );
            } while(!flag);

            baseFilter.push({
                'property': this.valueField,
                'value': value,
                'stage': stage
            });

            store.load({
                params: { filter: Ext.encode(baseFilter) },
                scope: this,
                callback: function() {
                    this.setValue(value, true);
                }
            });
        }
        else {
            core.fields.ComboField.superclass.setValue.call(this, value);
            if(value !== '' && value) this.markInvalid('O valor setado não existe.');
        }

        // console.debug('VALID VALUE: '+this.isValid(false));

        changedValid(this, value);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if(!cfg.rest && !cfg.store)
            throw 'Você precisa definir uma classe rest ou um Store para este combo.';
        else
            this.rest = cfg.rest;

        Ext.applyIf(
            cfg,
            {
                displayField: 'unicode',
                valueField: 'pk'
            }
        );

        if(!cfg.store)
            Ext.apply(
                cfg,
                {
                    store: this.getStore(cfg)
                }
            );

        Ext.apply(
            cfg,
            {
                queryParam: 'keyword',
                mode: 'remote',
                triggerAction: 'all',
                anyMatch: true,
            }
        );

        // this.callParent([cfg]);
        core.fields.ComboField.superclass.constructor.call(this, cfg);
        this.addEvents('changevalid');
    }
});
