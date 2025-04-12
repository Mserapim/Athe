Ext._define('rh.person.merge.GenericFieldSet', {
    extend: 'Ext.form.FieldSet',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        var scope = this;
        var items = [];
        var count = 1;
        cfg.field.values.forEach(function(subItem){
            var value = subItem.unicode;
            if(value == true)
                value = 'SIM';
            else if(value == false)
                value = 'NÃO';
            items.push(scope.factoryItemFieldSet({}, {
                name: cfg.field.name + '_' + count,
                value: value,
                valueRaw: subItem.raw_value,
                fieldLabel: cfg.field.label
            }));
            count += 1;
        });

        Ext.applyIf(
            cfg,
            {
                title: cfg.field.label,
                name: 'fieldset_' + cfg.field.name,
                items: items
            }
        );
        rh.person.merge.GenericFieldSet.superclass.constructor.call(this, cfg);
    },

    factoryItemFieldSet: function(cfg, params){
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            layout: 'hbox',
            border: false,
            items: [
                this.factoryFieldPanelCt({}, params),
                this.factoryCheckBoxPanelCt({}, params)
            ]
        });
        return Ext._create('Ext.Panel', cfg);
    },

    factoryFieldPanelCt: function(cfg, cfg_field){
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            layout: 'form',
            region: 'center',
            border: false,
            style: 'margin-left: 5px',
            items: this.factoryField(cfg_field)
        });
        return Ext._create('Ext.Panel', cfg);
    },

    factoryField: function(cfg){
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            width: 260,
            readOnly: true,
            enableKeyEvents: true,
            name: 'name',
            fieldLabel: 'Não definido',
        });
        return Ext._create('Ext.form.TextField', cfg);
    },

    factoryCheckBoxPanelCt: function(cfg, cfg_checkbox){
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            layout: 'form',
            region: 'center',
            border: false,
            style: 'margin-left: 10px',
            items: this.factoryCheckBox(cfg_checkbox)
        });
        return Ext._create('Ext.Panel', cfg);
    },

    factoryCheckBox: function(cfg){
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, {
            fieldLabel: 'Escolher',
            xtype: 'checkbox',
            name: 'check_' + cfg.name,
            field_name: cfg.name,
            width: 15,
            style: 'margin-left: -45px',
            listeners: {
                scope: this,
                check: function(fld, checked) {
                    this.onlyOneChecked(fld, checked);
                },
            },
        });
        return Ext._create('Ext.form.Checkbox', cfg);
    },

    onlyOneChecked: function(fld, checked){
        if(!this._prevent_reset_check){
            var scope =  this;
            var length_of = (fld.name.match(/_/g)||[]).length;
            var to_search = fld.name.split('_', length_of);
            for (var i = 0; i < length_of; i++)
                new_search = to_search[i];
            to_search = new_search;
            this.ownerCt.getForm().items.items.forEach(function(item){
                var length_of = (item.name.match(/_/g)||[]).length;
                var search = item.name.split('_', length_of);
                for (var i = 0; i < length_of; i++)
                    new_search = search[i];
                search = new_search;
                if(search == to_search && item.getValue() == true && fld.name != item.name){
                    scope._prevent_reset_check = true;
                    item.setValue(false);
                }
            });
        }
        this._prevent_reset_check = false;
    },
});
