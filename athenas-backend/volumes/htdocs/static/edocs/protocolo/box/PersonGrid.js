Ext._define('edocs.protocolo.box.PersonGrid', {
    extend: 'edocs.protocolo.box.MainGrid',

    __boxAction: 'inbox_person',

    simpleTitle: 'Pessoal',

    getDepartmentToolbarItem: function () {
        var item = edocs.protocolo.box.PersonGrid.superclass.getDepartmentToolbarItem.call(this, {});
        item.setHandler(function(){});
        return item;
    }
});
