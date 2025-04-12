/**
 *
 **/
 Ext._define("standard.fields.ChoiceField", {
    extend: "Ext.form.ComboBox",

    xtype: "choicefield",

    setValue: function (value, trigged) {
        var fireSelect = function (combo, value) {
            var index = combo.getStore().findExact(this.valueField, value, 0);
            var record = combo.getStore().getAt(index);
            var valid = record !== undefined;

            // console.debug('COMBO SET VALUE('+ (record !== undefined) +'): '+combo.startValue+'/'+record.id);
            if (valid) combo.fireEvent("select", combo, record, index, true);
        };

        var changedValid = function (cmb, value) {
            var index = cmb.getStore().findExact(this.valueField, value, 0);
            var record = cmb.getStore().getAt(index);
            var valid = record !== undefined;

            // console.debug('OV: '+cmb.value+' NV: '+value+' ORV:'+cmb.originalValue+' SV: '+cmb.startValue+' VALID: '+valid);

            if (!record || cmb.startValue !== record.id)
                cmb.fireEvent("changevalid", cmb, cmb.getValue(), cmb.startValue, valid);
        };

        trigged = core.nullValue(trigged, false);

        if (!isNaN(value) && value !== "") value = Ext.decode(value);

        if (value === 0) value = null;

        if (this.getStore().findExact(this.valueField, value, 0) >= 0 || trigged) {
            if (this.getStore().findExact(this.valueField, value, 0) >= 0 && value !== "") {
                standard.fields.ChoiceField.superclass.setValue.call(this, value);
                fireSelect(this, value);
            } else {
                standard.fields.ChoiceField.superclass.setValue.call(this, "");
                this.markInvalid("O valor não existe para ser relacionado.");
            }
        } else if (!trigged && value !== "" && value !== null) {
            var store = this.getStore();

            if (store.baseParams.keyword) delete store.baseParams.keyword;

            store.load({
                params: {
                    filter: Ext.encode([
                        {
                            property: "cache_path",
                            value: this.choiceId || this.mkChoiceId(this.choicePath),
                        },
                    ]),
                },
                scope: this,
                callback: function () {
                    this.setValue(value, true);
                },
            });
        } else {
            standard.fields.ChoiceField.superclass.setValue.call(this, value);
            if (value !== "" && value !== null) this.markInvalid("O valor setado não existe.");
        }

        // console.debug('VALID VALUE: '+this.isValid(false));

        changedValid(this, value);
    },

    mkChoiceId: function (choicePath) {
        return [choicePath.appLabel, choicePath.name].join(".");
    },

    getStore: function (cfg) {
        if (!this._store) {
            var restful = "standard.ChoiceRestful";
            if (cfg.filterOnlyActives && cfg.filterOnlyActives == true) {
                restful = "standard.ChoiceActiveRestful";
            }
            this._store = Ext._create(restful).getStore(false);

            var filter = [
                {
                    property: "cache_path",
                    value: cfg.choiceId || this.mkChoiceId(cfg.choicePath),
                },
            ];

            if (cfg.preFilter) {
                filter = filter.concat(cfg.preFilter);
            }

            this._store.baseParams.filter = Ext.encode(filter);
            this._store.baseParams.limit = 125;

            if (cfg.withNone || this.withNone)
                this._store.on({
                    scope: this,
                    load: function (store) {
                        store.insert(
                            0,
                            new Ext.data.Record({
                                value: cfg.defaultValue,
                                label: cfg.withNoneLabel || this.withNoneLabel,
                            })
                        );
                    },
                });
        }

        return this._store;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        if (!cfg.choiceId && !cfg.choicePath) throw "É necessário que se especifique ou o choideId ou o choicePath";

        Ext.applyIf(cfg, {
            withNone: false,
            withNoneLabel: "Indefinido",
            filterOnlyActives: true,
            valueField: "value",
            defaultValue:null
        });

        Ext.apply(cfg, {
            mode: "remote",
            triggerAction: "all",
            editable: false,
            lazyInit: false,
            typeAhead: true,
            typeAheadDelay: 750,
            displayField: "label",
            store: this.getStore(cfg),
        });

        // this.callParent([cfg]);
        standard.fields.ChoiceField.superclass.constructor.call(this, cfg);
    },
});
